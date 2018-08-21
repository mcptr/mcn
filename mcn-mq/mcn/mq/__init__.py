import os
import pika
import collections
import json
import time
import uuid
import socket
import mcn.core.logg
import mcn.core.errors
import bson.json_util


Exchange = collections.namedtuple(
    "Exchange",
    ["name", "exchange_type", "durable", "auto_delete"]
)


Queue = collections.namedtuple(
    "Queue",
    ["name", "durable", "auto_delete"]
)


ExclusiveQueue = collections.namedtuple("ExclusiveQueue", ["name"])


def mk_exclusive_queue(prefix):
    name = "%s@%s:%s:%s" % (
        prefix,
        socket.gethostname().replace(".", "_"),
        os.getpid(),
        str(uuid.uuid1()).split("-")[-1],
    )

    return ExclusiveQueue(name)


class InvalidMessageError(mcn.core.errors.Error):
    pass


class Message:
    def __init__(self, **kwargs):
        payload = (kwargs or dict())
        self.data = kwargs.pop("data", dict())
        self.meta = kwargs.pop("meta", dict())

        if "id" not in self.meta:
            self.update_meta(id=str(uuid.uuid4()))

        if "ctime" not in self.meta:
            self.update_meta(ctime=time.time())

    def __str__(self):
        return bson.json_util.dumps(dict(self), indent=4)

    def __repr__(self):
        return "%s:%s" % (self.__class__.__name__, self.meta["id"])

    def __getitem__(self, k):
        return self.data[k]

    def __iter__(self):
        yield "data", self.data
        yield "meta", self.meta

    def update(self, **kwargs):
        self.data.update(**kwargs)

    def update_meta(self, **kwargs):
        self.meta.update(**kwargs)

    def get(self, k, default_value=None):
        return self.data.get(k, default_value)

    def get_meta(self, k, default_value):
        return self.meta.get(k, default_value)


class IncomingMessage(Message):
    def __init__(self, ch, method, properties, serialized):
        super().__init__(**json.loads(serialized.decode()))
        self.channel = ch
        self.method = method
        self.properties = properties
        self.__is_handled = False

    def _raise_if_handled(self):
        if self.__is_handled:
            raise Exception("Message already ACK'ed/REJECT'ed")

    def reject(self, **kwargs):
        self._raise_if_handled()
        self.channel.basic_reject(
            delivery_tag=self.method.delivery_tag,
            requeue=kwargs.pop("requeue", False),
        )
        self.__is_handled = True

    def ack(self, **kwargs):
        self._raise_if_handled()
        self.channel.basic_ack(
            delivery_tag=self.method.delivery_tag
        )
        self.__is_handled = True

    # helper, wraps reject
    def requeue(self):
        self.reject(requeue=True)

    # helper, wraps reject
    def drop(self):
        self.reject(requeue=False)

    def is_handled(self):
        return self.__is_handled


class MQ:
    def __init__(self, exchange, queue=None, **kwargs):
        self.log = mcn.core.logg.get_logger(self.__class__.__name__)
        self.connection = kwargs.pop("connection", None)
        self.exchange = exchange
        self.queue = queue
        self.channel = None
        self.url = kwargs.pop("url", None)

        self.reconnect()

        if self.exchange:
            self.log.debug("DECLARE EXCHANGE: %s", self.exchange.name)
            self.channel.exchange_declare(
                exchange=self.exchange.name,
                exchange_type=self.exchange.exchange_type,
            )

        if self.queue:
            self.log.debug("DECLARE QUEUE: %s", self.queue.name)
            if isinstance(self.queue, ExclusiveQueue):
                queue = self.channel.queue_declare(
                    queue=(self.queue.name or ""),
                    exclusive=True
                )

                self.channel.queue_bind(
                    exchange=self.exchange.name,
                    queue=queue.method.queue,
                )
                self.log.debug("%s, %s", exchange.name, queue.method.queue)
            else:
                self.channel.queue_declare(
                    queue=self.queue.name,
                    durable=self.queue.durable,
                    auto_delete=self.queue.auto_delete,
                )

        if kwargs.get("bind_queue", False):
            rk = kwargs.pop("routing_key", self.queue.name)
            self.log.debug(
                "BIND: %s, %s, %s",
                self.exchange.name, self.queue.name, rk
            )
            self.channel.queue_bind(
                exchange=self.exchange.name,
                queue=self.queue.name,
                routing_key=rk,
            )

    def reconnect(self):
        if not self.connection or not self.connection.is_open:
            if not self.url:
                raise mcn.core.errors.Error("No url/connection")

            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.url)
            )

        self.channel = self.connection.channel()

    def __del__(self):
        if self.channel and self.channel.is_open:
            try:
                self.channel.close()
            except pika.exceptions.ChannelClosed as e:
                self.log.debug(e)

        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except pika.exceptions.ChannelClosed as e:
                self.log.debug(e)


class Producer(MQ):
    def __init__(self, exchange, queue=None, **kwargs):
        super().__init__(exchange, queue, **kwargs)
        self.channel.basic_qos(prefetch_count=1)

    # FIXME: when we have workers as consumers that consume and then
    # publish via producer instance - the producer connection may be
    # already closed due to inactivity - explore hearbeats, we're loosing messages
    # this way
    def publish(self, msg, **kwargs):
        properties = None
        if kwargs.pop("persistent", None):
            properties = pika.BasicProperties(
                delivery_mode=2,
                headers=kwargs.pop("headers", dict()),
            )

        routing_key = kwargs.pop("routing_key", self.queue.name)

        message = msg
        if not isinstance(msg, Message):
            message = Message()
            message.update(**msg)

        self.log.debug("-> %s::%s", self.exchange.name, routing_key)
        self.log.debug(str(message))
        self.channel.basic_publish(
            exchange=self.exchange.name,
            routing_key=routing_key,
            body=str(message),
            properties=properties,
        )


class Consumer(MQ):
    def __init__(self, exchange, queue, **kwargs):
        super().__init__(exchange, queue, **kwargs)
        self.callback = kwargs.pop("callback", self.on_message)

    def start(self, callback=None):
        callback = (callback or self.on_message)
        #self.log.info(callback.__name__)
        def _consume(ch, method, properties, body):
            im = IncomingMessage(ch, method, properties, body)
            self.log.debug(repr(im))

            try:
                callback(im, properties, method=method)
                if not im.is_handled():
                    im.ack()
            except InvalidMessageError as e:
                self.log.error(e)
                im.drop()
            except pika.exceptions.ConnectionClosed as e:
                self.log.error(e)

            except Exception as e:
                self.log.exception(e)
                # elog.audit("unhandled.error", str(e))

        self.log.info("Starting to consume")
        self.channel.basic_consume(_consume, queue=self.queue.name)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt as e:
            self.log.info("Interrupted, exiting.")
            return

    def on_message(self, im, properties, *args, **kwargs):
        self.log.info(dict(im))


class Worker:
    def __init__(self, consumer_config, producer_config, **kwargs):
        self.log = mcn.core.logg.get_logger(self.__class__.__name__)

        self.consumer_exchange = consumer_config["exchange"]
        self.consumer_queue = consumer_config.get("queue", None)
        self.consumer_url = consumer_config["url"]
        self.consumer_bind_queue = consumer_config.get("bind_queue", False)

        self.producer_exchange = producer_config["exchange"]
        self.producer_queue = producer_config.get("queue", None)
        self.producer_url = producer_config.get("url", None)
        self.producer_bind_queue = producer_config.get("bind_queue", False)

        if not self.consumer_queue:
            self.consumer_queue = mk_exclusive_queue(self.__class__.__name__)
            self.log.info(self.consumer_queue)
            self.consumer_bind_queue = False

        if not self.producer_queue:
            self.producer_queue = mk_exclusive_queue(self.__class__.__name__)
            self.log.info(self.consumer_queue)
            self.producer_bind_queue = False

        self.log.info("Initializing consumer")
        self.consumer = Consumer(
            self.consumer_exchange,
            self.consumer_queue,
            url=self.consumer_url,
            bind_queue=self.consumer_bind_queue,
        )

        self.log.info("Initializing producer")
        self.producer = Producer(
            self.producer_exchange,
            self.producer_queue,
            url=self.producer_url,
            connection=(
                self.consumer.connection if not self.producer_url else None
            ),
            bind_queue=self.producer_bind_queue,
        )

    def on_message(self, im, *args, **kwargs):
        self.log.debug(repr(im))

    def start(self):
        self.consumer.start(self.on_message)


if __name__ == "__main__":
    url = "amqp://guest:guest@localhost/mcn"
    test_exchange = Exchange("test", "direct", False, False)
    q_exclusive = ExclusiveQueue("exclusive")
    q_one = Queue("one", False, False)
    q_two = Queue("two", False, False)
    consumer = Consumer(test_exchange, q_one, url=url)
    producer = Producer(test_exchange, q_two, url=url)
    producer_sharing = Producer(test_exchange, q_one, connection=consumer.connection)
    assert (consumer.connection.is_open)
    assert (producer.connection.is_open)
    assert (producer_sharing.connection.is_open)


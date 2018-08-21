#!/usr/bin/env python

from mcn.scraper import Exchanges, Queues, settings
from mcn.mq import Producer
import mcn.core.logg


class Scheduler:
    def __init__(self, producer_config, **kwargs):
        self.log = mcn.core.logg.get_logger(self.__class__.__name__)
        self.producer = Producer(
            exchange=producer_config["exchange"],
            queue=producer_config["queue"],
            url=producer_config.get("url", settings.SCRAPER_AMQP_URL),
            bind_queue=producer_config.get("bind_queue", True)
        )

    def gen_jobs(self):
        raise Exception("Not implemented")

    def start(self):
        try:
            for job in self.gen_jobs():
                self.producer.publish(job, persistent=True)
        except KeyboardInterrupt as e:
            print("Interrupted\n")
            return


class URLScheduler(Scheduler):
    def __init__(self, **kwargs):
        super().__init__(
            dict(
                exchange=Exchanges.URLS,
                queue=Queues.URLS_NEW,
                url=settings.SCRAPER_AMQP_URL,
                bind_queue=True,
            )
        )


class DocumentScheduler:
    def __init__(self, **kwargs):
        super().__init__(
            dict(
                exchange=Exchanges.DOWNLAOD,
                queue=Queues.DOWNLOAD_DOCUMENT,
                url=settings.SCRAPER_AMQP_URL,
                bind_queue=True
            )
        )

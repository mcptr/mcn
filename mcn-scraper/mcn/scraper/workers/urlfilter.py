#!/usr/bin/env python

from mcn.scraper import Exchanges, Queues, settings
from mcn.mq import Worker
import mcn.core.logg


class URLFilter(Worker):
    def __init__(self, **kwargs):
        super().__init__(
            dict(
                exchange=Exchanges.URLS,
                queue=Queues.URLS_NEW,
                url=settings.SCRAPER_AMQP_URL,
                bind_queue=True,
            ),
            dict(
                exchange=Exchanges.DOWNLOAD,
                queue=Queues.DOWNLOAD_HEAD,
                bind_queue=True,
            )
        )

    def on_message(self, im, properties, *args, **kwargs):
        self.log.info(im)
        self.producer.publish(im, persistent=True, headers=properties.headers)
        im.ack()

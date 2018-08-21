#!/usr/bin/env python

from mcn.scraper import Exchanges, Queues, settings
from mcn.mq import Producer, Consumer, Message

import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--timeout", default=3, type=float)
parser.add_argument("url", nargs="+")


if __name__ == "__main__":
    args = parser.parse_args()

    producer = Producer(
        Exchanges.URLS,
        Queues.URLS_NEW,
        url=settings.SCRAPER_AMQP_URL,
    )

    for url in args.url:
        msg = Message()
        msg.update(url=url)
        msg.update_meta(timeout=args.timeout)
        producer.publish(msg, persistent=True)

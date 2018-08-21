#!/usr/bin/env python

from mcn.scraper import Exchanges, Queues, settings
from mcn.mq import Producer, Message

import argparse


parser = argparse.ArgumentParser()

parser.add_argument(
    "-F", "--force",
    action="store_true", help="Skip throttling"
)

parser.add_argument("-t", "--timeout", type=float, default=0)
parser.add_argument("url", nargs="+")


if __name__ == "__main__":
    args = parser.parse_args()

    producer = Producer(
        Exchanges.DOWNLOAD,
        Queues.DOWNLOAD_DOCUMENT,
        url=settings.SCRAPER_AMQP_URL,
    )

    for url in args.url:
        msg = Message()
        msg.update(url=url)
        msg.update_meta(timeout=args.timeout)
        headers = dict()
        if args.force:
            headers.update(skip_throttling=True)
        producer.publish(msg, persistent=True, headers=headers)

#!/usr/bin/env python

from mcn.scraper.db import DB, urls
from mcn.scraper.workers import scheduler
import os
import time
import argparse


class URLScheduler(scheduler.URLScheduler):
    def __init__(self, db, *args, **kwargs):
        self.db = db
        self.batch_size = kwargs.pop("batch_size", 32)
        self.delay = kwargs.pop("delay", 0)
        super().__init__(*args, **kwargs)

    def gen_jobs(self):
        while True:
            batch = 0
            records = []
            while True:
                with self.db.conn.cursor() as cur:
                    self.log.info("Batch: %d", batch)
                    records = urls.select_urls_to_revisit(
                        cur,
                        age=3600,
                        offset=(batch * self.batch_size),
                        limit=self.batch_size
                    )

                    for r in records:
                        if "text/html" in r.content_type:
                            self.log.info(r.url)
                            yield r._asdict()
                    time.sleep(self.delay)

                batch = 0 if not records else batch + 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--age", type=int, default=3600)
    parser.add_argument("-b", "--batch-size", type=int, default=2)
    parser.add_argument("-d", "--delay", type=float, default=1)

    args = parser.parse_args()

    db = DB(os.environ["PGSQL_URL"])
    urls.initialize(db.conn.cursor())

    worker = URLScheduler(
        db,
        batch_size=args.batch_size,
        delay=args.delay,
    )

    worker.start()

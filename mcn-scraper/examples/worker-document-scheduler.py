#!/usr/bin/env python

from mcn.scraper.workers import scheduler


class URLScheduler(scheduler.URLScheduler):
    def gen_jobs(self):
        for i in range(3):
            yield dict(
                url="http://localhost/feed/me/please",
            )


if __name__ == "__main__":
    worker = URLScheduler()
    worker.start()

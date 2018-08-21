#!/usr/bin/env python

from mcn.scraper.workers.download import document


class Downloader(document.Downloader):
    def on_success(self, im, *args, **kwargs):
        self.log.info(str(im))

    def on_error(self, im, *args, **kwargs):
        self.log.error(str(im))


if __name__ == "__main__":
    downloader = Downloader(enable_cache=True)
    downloader.start()

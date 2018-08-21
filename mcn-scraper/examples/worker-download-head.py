#!/usr/bin/env python


from mcn.scraper.workers.download import head


class Downloader(head.Downloader):
    def on_success(self, im, parsed, *args, **kwargs):
        self.log.info(str(im))

    def on_error(self, im, parsed, *args, **kwargs):
        self.log.error(str(im))


if __name__ == "__main__":
    downloader = Downloader()
    downloader.start()

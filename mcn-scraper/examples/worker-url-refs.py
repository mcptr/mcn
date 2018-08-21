#!/usr/bin/env python

from mcn.scraper.workers import urlrefs


class URLRefs(urlrefs.URLRefsConsumer):
    def pre_process(self, im, parsed, *args, **kwargs):
        pass

    def process_ref(self, parsed_ref, parsed_parsent, *args, **kwargs):
        # store them in db, for example
        pass


if __name__ == "__main__":
    worker = URLRefs()
    worker.start()

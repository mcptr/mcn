#!/usr/bin/env python

from mcn.scraper.workers import urlfilter
from mcn.core import logg
from urllib.parse import urlparse


log = logg.get_logger(__name__)


class URLFilter(urlfilter.URLFilter):
    pass


if __name__ == "__main__":
    worker = URLFilter()
    worker.start()

from mcn.mq import (Exchange, Queue, Producer, Consumer)

__version__ = "0.0.1"


class Exchanges:
    URLS = Exchange("scraper.urls.direct", "direct", True, False)
    DOWNLOAD = Exchange("scraper.download.direct", "direct", True, False)
    HEADERS = Exchange("scraper.headers.fanout", "fanout", True, False)
    DOCUMENTS = Exchange("scraper.documents.fanout", "fanout", True, False)


class Queues:
    URLS_NEW = Queue("scraper:urls:new", True, False)

    DOWNLOAD_HEAD = Queue("scraper:download:head", True, False)
    DOWNLOAD_DOCUMENT = Queue("scraper:download:document", True, False)

    HEADERS_ALL = Queue("scraper:headers:all", True, False)
    DOCUMENTS_ALL = Queue("scraper:documents:all", True, False)

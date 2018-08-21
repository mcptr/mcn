import logging
import datetime
import collections
import requests


Result = collections.namedtuple(
    "Result", ["url", "title", "description"]
)


class Provider:
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.log = logging.getLogger(self.name)
        self.session = requests.Session()
        self.session.headers.update(kwargs.pop("headers", dict()))
        self.log.info(self.session.headers)

    def search(self, term, product=None):
        product = dict() if product is None else product
        self.log.debug(term)

        product[self.name] = dict()

        start_time = datetime.datetime.now()
        results = dict()
        try:
            results = self.run_search(term, product[self.name])
        except AttributeError as e:
            self.log.error(e)
        end_time = datetime.datetime.now()

        product[self.name].update(
            time_us=(end_time - start_time).microseconds,
            results=results,
        )

    def decode_content(self, response):
        return response.text.encode("ascii", "ignore").decode("utf-8")

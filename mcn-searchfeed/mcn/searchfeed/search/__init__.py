import uuid
import json
import time


class Product:
    def __init__(self, term=None):
        self.term = (term or str())
        self.id = str(uuid.uuid1())
        self.ctime = time.time()
        self.providers = dict()
        self.pre_processing = dict()
        self.post_processing = dict()

    def _asdict(self):
        return self.__dict__


class Search:
    def __init__(self, **kwargs):
        self.hooks_before = kwargs.pop("before", [])
        self.hooks_after = kwargs.pop("after", [])
        self.providers = kwargs.pop("providers", [])

    def before(self, *args):
        for arg in args:
            assert callable(arg)
            self.hooks_before.append(arg)

    def after(self, *args):
        for arg in args:
            assert callable(arg)
            self.hooks_after.append(arg)

    def __call__(self, q):
        product = Product(q)
        if not q:
            return product

        for item in self.hooks_before:
            item(q, product.pre_processing)

        for provider in self.providers:
            provider.search(q, product.providers)

        for item in self.hooks_after:
            item(q, product.post_processing)

        return product

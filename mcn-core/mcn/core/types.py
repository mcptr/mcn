import bson.json_util

class Meta:
    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __getitem__(self, k):
        return self.__dict__[k]

    def __iter__(self):
        for k in self.__dict__:
            item = self.__dict__[k]
            if callable(item):
                if isintance(item, Meta):
                    yield k, item
            else:
                yield k, item

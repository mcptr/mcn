class Processor:
    NAME = None

    def name(self):
        return (self.NAME or self.__class__.__name__.lower())

    def __call__(self, term, properties):
        properties[self.name()] = self.process(term)


class Group:
    def __init__(self, name, processors):
        self.name = name
        for p in processors:
            assert callable(p)
        self.processors = processors

    def __call__(self, term, properties):
        properties[self.name] = dict()
        for proc in self.processors:
            proc(term, properties[self.name])


class Length(Processor):
    def process(self, term):
        return len(term)


def word_count(term, product):
    product["word_count"] = len(term.split(" "))

class Analyzer:
    def __init__(self, name, **kwargs):
        self.name = name
        self.pre_processors = kwargs.pop("pre_processors", [])
        self.processors = kwargs.pop("processors", [])

    def __call__(self, in_product):
        result = dict()
        result[self.name] = dict()

        for pre_proc in self.pre_processors:
            in_product = pre_proc(in_product)

        for proc in self.processors:
            name = None
            if isinstance(proc, Analyzer):
                result[self.name].update(proc(in_product))
            else:
                try:
                    name = proc.name
                except:
                    name = proc.__name__

                result[self.name][name] = proc(in_product)
        return result

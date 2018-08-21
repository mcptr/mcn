from . import provider


class Mechanoia(provider.Provider):
    def run_search(self, term, product):
        return [
            # provider.Result(
            #     "https://example.com",
            #     "Dummy title",
            #     "Dummy description"
            # )
        ]

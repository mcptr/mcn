#!/usr/bin/env python


import os
import sys
import json
import code
import logging
import atexit
import readline

from mcn.searchfeed import processors
from mcn.searchfeed import search

from mcn.searchfeed.search.providers.bing import BingHTML
from mcn.searchfeed.search.providers.ecosia import EcosiaHTML
from mcn.searchfeed.search.providers.duckduckgo import DuckDuckGoHTML
from mcn.searchfeed.search.providers.mechanoia import Mechanoia


LOG_FORMAT = (
    "[%(asctime)s] %(levelname)s [%(filename)s.%(name)s.%(funcName)s:%(lineno)s:] %(message)s"
)

log = logging.getLogger(__name__)


class Cli(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>",
                 histfile=os.path.expanduser("~/.mcn-searchfeed"),
                 **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except FileNotFoundError:
                pass
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.set_history_length(1000)
        readline.write_history_file(histfile)

    def run(self, callback):
        q = input("\n> ")
        return callback(q)


def dump_results(product):
    for provider in product.providers:
        p = product.providers[provider]
        print(provider)
        for r in p.get("results", []):
            print("\t", r.url)


if __name__ == "__main__":
    s = search.Search(
        providers=[
            DuckDuckGoHTML(),
            EcosiaHTML(),
            BingHTML(),
            # Mechanoia(),
        ],
        before=[
            processors.Group(
                "text",
                [
                    processors.Length(),
                    processors.word_count,
                ]
            )
        ]
    )


    if len(sys.argv) > 1:
        product = s(" ".join(sys.argv[1:]))
        print(json.dumps(product._asdict(), indent=4))
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            stream=sys.stdout,
            format=LOG_FORMAT,
        )

        cli = Cli()

        while True:
            try:
                product = cli.run(s)
                if product:
                    dump_results(product)
            except (KeyboardInterrupt, EOFError) as e:
                log.info("\n# Exiting")
                break

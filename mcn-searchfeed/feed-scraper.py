#!/usr/bin/env python

from mcn.searchfeed import settings
from mcn.searchfeed import processors
from mcn.searchfeed import search

from mcn.searchfeed.search.providers.bing import BingHTML
from mcn.searchfeed.search.providers.ecosia import EcosiaHTML
from mcn.searchfeed.search.providers.duckduckgo import DuckDuckGoHTML
from mcn.searchfeed.search.providers.mechanoia import Mechanoia
import mcn.scraper
import mcn.scraper.settings
from mcn.scraper.utils import user_agent
import mcn.mq

import os
import sys
import json
import time
import logging


LOG_FORMAT = (
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:] %(message)s"
)

LOG_FORMAT = (
    "[%(asctime)s] %(levelname)s [%(filename)s.%(name)s.%(funcName)s:%(lineno)s:] %(message)s"
)

log = logging.getLogger(__name__)


# logging.basicConfig(
#     level=logging.INFO,
#     stream=sys.stdout,
#     format=LOG_FORMAT,
# )


producer = mcn.mq.Producer(
    mcn.scraper.Exchanges.DOWNLOAD,
    mcn.scraper.Queues.DOWNLOAD_HEAD,
    url=mcn.scraper.settings.AMQP_URL,
)


s = search.Search(
    providers=[
        DuckDuckGoHTML(headers={"user-agent": user_agent.get_random()}),
        EcosiaHTML(headers={"user-agent": user_agent.get_random()}),
        # BingHTML(headers={"user-agent": user_agent.get_random()}),
        # Mechanoia(),
    ],
)

search_term = " ".join(sys.argv[1:])
product = s(search_term)
print(json.dumps(product._asdict(), indent=4))
for provider in product.providers:
    p = product.providers[provider]
    for r in (p.get("results", []) or []):
        msg = dict(
            url=r.url,
            ctime=time.time(),
            feed="mcn-searchfeed",
            searchfeed_provider=provider,
            search_term=search_term,
        )
        print(msg)
        producer.publish(msg)

import random
from urllib.parse import urlparse
from mcn.searchfeed.analysis.analyzer import Analyzer
from mcn.searchfeed import processors


def fqdn(parsed_url):
    return parsed_url.hostname


def scheme(parsed_url):
    return parsed_url.scheme


def domain_keywords(parsed_url):
    return parsed_url.hostname.split(".")


def tld(parsed_url):
    return parsed_url.hostname.split(".")[-1]


def document_type(parsed_url):
    filename = parsed_url.path.split("/").pop()
    pos = filename.rfind(".")
    return filename[pos + 1:] if pos > 1 else None


def url_keywords(parsed_url):
    parts = parsed_url.path.split("/")
    keywords = []
    for kwl in map(lambda p: p.split("-"), parts):
        keywords.extend(kwl)
    return list(set(filter(len, keywords)))


url_analyzer = Analyzer(
    "analysis.url",
    processors=[
        len,
        Analyzer(
            "details",
            pre_processors=[urlparse],
            processors=[
                fqdn,
                scheme,
                domain_keywords,
                tld,
                document_type,
                url_keywords,
            ]
        )
    ]
)


def process(search_product):
    urls = dict()
    for p in search_product.providers:
        results = search_product.providers[p].get("results", [])
        for i in range(len(results)):
            r = results[i]
            urls.setdefault(r.url, dict(
                providers=dict(),
            ))
            urls[r.url]["providers"][p] = dict(
                pos=i,
                description=r.description
            )

    analyzers = [url_analyzer]
    for anl in analyzers:
        for url in urls:
            urls[url].update(url_analyzer(url))

    return urls

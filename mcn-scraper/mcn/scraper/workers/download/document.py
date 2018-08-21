#!/usr/bin/env python

import mcn.scraper
from mcn.scraper import settings
from mcn.scraper import downloader
from mcn.scraper.parser import html_document
from mcn.mq import Worker
import mcn.core.storage

import hashlib
import uuid
from datetime import datetime
from urllib.parse import urlparse


class Downloader(Worker, downloader.Downloader):
    def __init__(self, *args, **kwargs):
        Worker.__init__(
            self,
            dict(
                exchange=mcn.scraper.Exchanges.DOWNLOAD,
                queue=mcn.scraper.Queues.DOWNLOAD_DOCUMENT,
                bind_queue=True,
                url=settings.SCRAPER_AMQP_URL,
            ),
            dict(
                exchange=mcn.scraper.Exchanges.DOCUMENTS,
                queue=mcn.scraper.Queues.DOCUMENTS_ALL,
                bind_queue=True,
            ),
            **kwargs
        )
        downloader.Downloader.__init__(self, **kwargs)
        self.db = None
        if kwargs.pop("enable_cache", None) or kwargs.get("cache_url", None):
            mongo_client = mcn.core.storage.connect_mongo(
                kwargs.pop("cache_url", settings.MONGODB_URL)
            )
            self.db = mongo_client.get_default_database()

    def parse_document(self, response):
        if "text/html" in response.headers.get("Content-Type", ""):
            return html_document.parse(response.text)
        return None

    def on_success(self, im, *args, **kwargs):
        pass

    def on_error(self, im, *args, **kwargs):
        pass

    def on_message(self, im, properties, **kwargs):
        url = im["url"]
        parsed = urlparse(url)
        fqdn = parsed.hostname

        if  not properties.headers.get("skip_throttling", None):
            if self.is_url_throttled(url):
                self.log.warning("Throttled URL: %s", url)
                im.drop()
                return

            if self.is_domain_throttled(fqdn):
                self.log.warning("Throttled FQDN: %s", fqdn)
                im.drop()
                return

        errors = dict()
        response = None
        try:
            response = self.fetch(url, errors=errors)
        except downloader.InvalidRequestError as e:
            self.log.error(e)

        self.throttle_url(url)
        self.throttle_domain(fqdn)

        cache_id = None
        parsed_document = None

        if not response:
            im.drop()
            self.on_error(im)
        elif response.ok:
            parsed_document = self.parse_document(response)
            im.update(parsed=parsed_document)

            if self.db:
                cache_id = hashlib.md5(url.encode()).hexdigest()
                record = self.db.documents.update(
                    dict(_id=cache_id),
                    dict(
                        url=url,
                        content=response.text,
                        parsed=parsed_document,
                        fetched_on=datetime.utcnow(),
                    ),
                    upsert=True,
                )
                im.update(cache_id=cache_id)

            self.on_success(im, **kwargs)
            self.producer.publish(im, persistent=True)
            self.log.info("%s, cache_id: %s, %s", response, cache_id, url)
            im.ack()

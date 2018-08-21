#!/usr/bin/env python

from mcn.scraper import Exchanges, Queues
from mcn.scraper import settings
from mcn.scraper import downloader
from mcn.scraper.db import DB, domains, urls
from mcn.scraper.utils import user_agent
from mcn.mq import Worker

from urllib.parse import urlparse
from datetime import datetime
import json


class Downloader(Worker, downloader.Downloader):
    def __init__(self, **kwargs):
        Worker.__init__(
            self,
            dict(
                exchange=Exchanges.DOWNLOAD,
                queue=Queues.DOWNLOAD_HEAD,
                url=settings.SCRAPER_AMQP_URL,
                bind_queue=True,
            ),
            dict(
                exchange=Exchanges.HEADERS,
                queue=Queues.HEADERS_ALL,
                bind_queue=True,
            ),
            **kwargs
        )
        downloader.Downloader.__init__(self, **kwargs)

        self.db = DB(settings.SCRAPER_PGSQL_URL)

        domains.initialize(self.db.conn.cursor())
        urls.initialize(self.db.conn.cursor())

    def store(self, im, parsed_url, **kwargs):
        try:
            with self.db.conn.cursor() as cur:
                r = domains.store_domain(cur, parsed_url.hostname)
                params = dict(
                    url=im["url"],
                    domain_id=r.id,
                    headers=im["headers"],
                    content_type=im.get_meta("content_type", None),
                    content_size=im.get_meta("content_length", None),
                )
                r = urls.store_url(cur, params)
                if r:
                    self.log.info("Saved: %s", r.id)
                cur.connection.commit()
        except DB.Error as e:
            self.log.exception(e)

    def on_message(self, im, properties, **kwargs):
        url = im["url"]
        parsed_url = urlparse(url)
        fqdn = parsed_url.hostname

        if not properties.headers.get("skip_throttling", False):
            if self.is_url_throttled(url):
                self.log.warning("Throttled URL: %s", url)
                im.drop()
                return

            if self.is_domain_throttled(fqdn):
                self.log.warning("Throttled FQDN: %s", fqdn)
                im.drop()
                return

        errors = {}
        response = None

        try:
            response = self.fetch_head(
                url,
                timeout=im.get("timeout", None),
                headers={"User-Agent": user_agent.get_random()},
                errors=errors,
            )
            self.log.info("%s, %s", response, response.url)
        except downloader.InvalidRequestError as e:
            self.log.error(e)

        self.throttle_url(url)
        self.throttle_domain(fqdn)

        if not response:
            im.update_meta(
                head_errors=errors,
            )
        else:
            im.update(headers=dict(response.headers))
            im.update_meta(
                head_time_us=response.elapsed.microseconds,
                head_status_code=response.status_code,
                last_visit_head=datetime.utcnow(),
                **{
                    "content_type": response.headers.get("content-type", None),
                    "content_length": response.headers.get("content-length", None)
                },
            )

        self.store(im, parsed_url)
        self.producer.publish(im, persistent=True)
        if response:
            self.on_success(im, parsed_url, **kwargs)
            im.ack()
        else:
            self.on_error(im, parsed_url)
            im.drop()

    def on_success(self, im, parsed_url, *args, **kwargs):
        pass

    def on_error(self, im, parsed_url, *args, **kwargs):
        pass

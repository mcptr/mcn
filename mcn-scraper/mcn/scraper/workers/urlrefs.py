#!/usr/bin/env python


import mcn.scraper
from  mcn.scraper import settings
from  mcn.mq import Worker, Consumer, mk_exclusive_queue
from urllib.parse import urlparse, urljoin


class InvalidRefURL(Exception):
    pass


class URLRefsConsumer(Consumer):
    def __init__(self, **kwargs):
        kwargs.setdefault("url", settings.SCRAPER_AMQP_URL)
        super().__init__(
            mcn.scraper.Exchanges.DOCUMENTS,
            mk_exclusive_queue(self.__class__.__name__),
            **kwargs
        )

    def on_message(self, im, properties, *args, **kwargs):
        url = im["url"]
        print(im)
        parsed = urlparse(url)
        fqdn = parsed.hostname
        try:
            self.pre_process(im, parsed, **kwargs)

            refs = im.get("parsed", {}).get("links", [])
            for ref in refs:
                href = ref.get("href", None)
                text = ref.get("text", None)
                if not href:
                    continue
                fullurl = urljoin(url, href)
                parsed_ref = urlparse(fullurl)
                try:
                    self.process_ref(parsed_ref, parsed)
                    self.log.info("%s\t%s", text, fullurl)
                except InvalidRefURL as e:
                    self.log.exception(e)
                    im.drop()
                    continue

            im.ack()
        except Exception as e:
            self.log.exception(e)
            im.drop()

    def pre_process(self, im, parsed, **kwargs):
        pass

    def process_ref(self, parsed_ref_url, parsed_parent_url, **kwargs):
        if parsed_ref_url.scheme not in ["http", "https"]:
            raise InvalidRefURL()


class URLRefsForwarder(Worker):
    def __init__(self, **kwargs):
        super().__init__(
            dict(
                exchange=mcn.scraper.Exchanges.DOCUMENTS,
                url=settings.SCRAPER_AMQP_URL,
                bind_queue=True,
            ),
            dict(
                exchange=mcn.scraper.Exchanges.URLS,
                queue=mcn.scraper.Queues.URLS_NEW,
                bind_queue=True,
            ),
        )

    def pre_process(self, im, parsed, **kwargs):
        pass

    def process_ref(self, parsed_ref_url, parsed_parent_url, **kwargs):
        if parsed_ref_url.scheme not in ["http", "https"]:
            raise InvalidRefURL()

    def on_message(self, im, properties, *args, **kwargs):
        url = im["url"]
        parsed = urlparse(url)
        fqdn = parsed.hostname
        try:
            self.pre_process(im, parsed, **kwargs)

            refs = im.get("parsed", {}).get("links", [])
            for ref in refs:
                href = ref.get("href", None)
                text = ref.get("text", None)
                if not href:
                    continue
                fullurl = urljoin(url, href)
                parsed_ref = urlparse(fullurl)
                try:
                    self.process_ref(parsed_ref, parsed)
                    self.log.info("%s\t%s", text, fullurl)
                    if self.producer:
                        msg = dict(
                            url=fullurl,
                            parent=url,
                            feed="scraper.urlrefs",
                        )

                        self.producer.publish(msg, persistent=True)
                except InvalidRefURL as e:
                    self.log.exception(e)
                    im.drop()
                    continue

            im.ack()
        except Exception as e:
            self.log.exception(e)
            im.drop()

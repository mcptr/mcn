from mcn.scraper import settings, cache
import mcn.core.logg
import mcn.core.errors


import requests
from datetime import datetime


DEFAULT_TIMEOUT_HEAD = 3
DEFAULT_TIMEOUT = 5


class InvalidRequestError(mcn.core.errors.Error):
    pass


class InvalidUrlError(mcn.core.errors.Error):
    pass


class Downloader:
    def __init__(self, **kwargs):
        self.log = mcn.core.logg.get_logger(self.__class__.__name__)
        self.headers = kwargs.pop("headers", dict())
        self.redis = cache.get_redis(
            kwargs.pop("redis_url", settings.SCRAPER_REDIS_URL)
        )

    def mk_domain_throttling_key(self, fqdn):
        return "throttle:fqdn:%s" % fqdn

    def mk_url_throttling_key(self, url):
        return "throttle:url:%s" % url

    def is_domain_throttled(self, fqdn):
        return self.redis.get(self.mk_domain_throttling_key(fqdn))

    def is_url_throttled(self, url):
        return self.redis.get(self.mk_url_throttling_key(url))

    def throttle_url(self, url, ttl=3600):
        self.redis.setex(self.mk_url_throttling_key(url), ttl, 1)

    def throttle_domain(self, fqdn, ttl=60):
        self.redis.setex(self.mk_domain_throttling_key(fqdn), ttl, 1)

    def fetch_head(self, url, **kwargs):
        timeout = float(kwargs.pop("timeout", 0) or DEFAULT_TIMEOUT_HEAD)
        headers = self.headers.copy()
        headers.update(kwargs.pop("headers", dict()))
        errors = kwargs.pop("errors", dict())
        try:
            response = requests.head(
                url,
                headers=headers,
                params=kwargs.pop("params", {}),
                timeout=timeout,
                allow_redirects=True,
                # verify=False,  # FIXME: collect the sites with ssl issues
            )

            return response
        except requests.exceptions.SSLError as e:
            self.log.exception(e)
            errors.update(ssl_error=1)
            raise InvalidRequestError(e)
        except requests.exceptions.ConnectionError as e:
            self.log.error(e)
            errors.update(connection_error=1)
            # FIXME: counter
            raise InvalidRequestError(e)
        except requests.exceptions.InvalidSchema as e:
            self.log.error(e)
            errors.update(invalid_schema=1)
            # FIXME: mining, mailto:, etc
            raise InvalidRequestError(e)
        except requests.exceptions.MissingSchema as e:
            raise InvalidRequestError(e)

    def fetch(self, url, **kwargs):
        timeout = float(kwargs.pop("timeout", 0) or DEFAULT_TIMEOUT)
        headers = self.headers.copy()
        headers.update(kwargs.pop("headers", dict()))
        errors = kwargs.pop("errors", dict())
        try:
            response = requests.get(
                url,
                headers=headers,
                params=kwargs.pop("params", {}),
                timeout=timeout,
                allow_redirects=True,
                # verify=False,  # FIXME: collect the sites with ssl issues
            )
            return response
        except requests.exceptions.SSLError as e:
            self.log.exception(e)
            errors.update(ssl_error=1)
            raise InvalidRequestError(e)
        except requests.exceptions.ConnectionError as e:
            self.log.error(e)
            errors.update(connection_error=1)
            # FIXME: counter
            raise InvalidRequestError(e)
        except requests.exceptions.InvalidSchema as e:
            self.log.error(e)
            errors.update(invalid_schema=1)
            # FIXME: mining, mailto:, etc
            raise InvalidRequestError(e)
        except requests.exceptions.MissingSchema as e:
            raise InvalidUrlError(e)

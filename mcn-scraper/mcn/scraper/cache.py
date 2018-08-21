from mcn.scraper import settings
from redis import StrictRedis
from urllib.parse import urlparse


def get_redis(url=None):
    url = (url or settings.SCRAPER_REDIS_URL)
    url = urlparse(settings.SCRAPER_REDIS_URL)
    return StrictRedis(
        host=url.hostname,
        db=int(url.path.lstrip("/"))
    )


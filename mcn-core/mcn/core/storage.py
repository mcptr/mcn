import os
import mcn.core.logg
import pymongo
import psycopg2
from psycopg2.extras import NamedTupleCursor


MONGODB_URL = os.environ.get(
    "MONGODB_URL",
    "mongodb://mcn:mcn@localhost/mcn"
)


PGSQL_URL = os.environ.get(
    "PGSQL_URL",
    "postgresql://localhost/mcn"
)


log = mcn.core.logg.get_logger(__name__)


def connect_mongo(url=MONGODB_URL):
    return pymongo.MongoClient(url)


def connect_pgsql(url=PGSQL_URL):
    return psycopg2.connect(
        url,
        cursor_factory=NamedTupleCursor
    )


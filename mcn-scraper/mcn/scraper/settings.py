import os


SCRAPER_AMQP_URL = os.environ.get(
    "SCRAPER_AMQP_URL",
    "amqp://guest:guest@localhost"
)

SCRAPER_REDIS_URL = os.environ.get(
    "SCRAPER_REDIST_URL",
    "redis://localhost/0"
)

SCRAPER_PGSQL_URL = os.environ.get(
    "SCRAPER_PGSQL_URL",
    "dbname=mcn",
)

# MONGODB_URL = os.environ.get(
#     "MONGODB_URL",
#     "mongodb://mcn:mcn@localhost/mcn"
# )

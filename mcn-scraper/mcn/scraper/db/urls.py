import mcn.core.logg
import os
from psycopg2.extras import Json


log = mcn.core.logg.get_logger(__name__)


def read_sql(*name):
    path = os.path.join(os.path.dirname(__file__), "sql", *name)
    log.info("Reading SQL: %s", path)
    return open(path, "r").read()


SQL_PREPARE_STORE_URL = read_sql("prepare_store_url.sql")
SQL_EXECUTE_STORE_URL = read_sql("execute_store_url.sql")
SQL_SELECT_URLS_TO_REVISIT = read_sql("select_urls_to_revisit.sql")


def initialize(cur):
    cur.execute(SQL_PREPARE_STORE_URL)


def store_url(cur, params):
    headers = params.get("headers", None)
    params["headers"] = Json(headers) if headers else None
    cur.execute(SQL_EXECUTE_STORE_URL, params)
    return cur.fetchone()


def select_urls_to_revisit(cur, **params):
    cur.execute(SQL_SELECT_URLS_TO_REVISIT, params)
    return cur.fetchall()

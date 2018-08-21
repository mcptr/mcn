from mcn.core.storage import connect_pgsql
import psycopg2


class DB:
    Error = psycopg2.Error

    def __init__(self, url):
        self.conn = connect_pgsql(url)

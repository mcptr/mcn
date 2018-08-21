SQL_INSERT_DOMAIN = " ".join([
    "PREPARE st_insert_domain AS"
    "  INSERT INTO domains AS D(fqdn) VALUES($1)"
    "    ON CONFLICT(fqdn) DO UPDATE SET mtime = NOW(), hits = D.hits + 1"
    "    RETURNING *"
])


def initialize(cur):
    cur.execute(SQL_INSERT_DOMAIN)


def store_domain(cur, fqdn):
    cur.execute("EXECUTE st_insert_domain(%s)", (fqdn,))
    return cur.fetchone()

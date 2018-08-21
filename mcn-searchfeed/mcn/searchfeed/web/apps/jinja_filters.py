import uuid
from urllib.parse import urlparse


def em_fqdn(url):
    p = urlparse(url)
    url = """%s://<span class="fqdn">%s</span>%s""" % (
        p.scheme, p.hostname, p.path
    )

    url += "?%s" % p.query if p.query else ""
    return url


def register(app):
    app.jinja_env.filters["em_fqdn"] = em_fqdn
    app.jinja_env.globals.update(gen_uuid=lambda: str(uuid.uuid4()))


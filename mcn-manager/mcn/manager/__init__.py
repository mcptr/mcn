import os
import requests
import uuid
import hashlib
import json
import base64
import random

from collections import namedtuple

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gen_random_string(n=8, prefix=None):
    s = "".join(random.choice(ALPHABET) for _ in range(n))
    if prefix:
        return (str(prefix) + "-" + s)
    return s


Vhost = namedtuple(
    "Vhost",
    ["name"]
)


User = namedtuple(
    "User",
    ["user", "password"]
)


_Cluster = namedtuple(
    "Cluster",
    ["host", "user", "password", "port", "api_port", "secure"]
)


class Cluster:
    def __init__(self, config):
        config.setdefault("port", 5672)
        config.setdefault("api_port", 15672)
        config.setdefault("secure", True)
        self.data = _Cluster(**config)

    def get_amqp_url(self, **kwargs):
        params = self.data._asdict()

        user = kwargs.pop("user", None)
        print("USER", user)
        if user:
            params.update(user._asdict())

        vhost = kwargs.pop("vhost", None)
        vhost = vhost.name if isinstance(vhost, Vhost) else None
        url = "amqp://{user}:{password}@{host}:{port}".format(**params)
        return "/".join([url, vhost]) if vhost else url

    def get_api_url(self):
        return "{scheme}://{user}:{password}@{host}:{api_port}/api".format(
            scheme=("https" if self.data.secure else "http"),
            **self.data._asdict()
        )


class RabbitMQManager:
    def __init__(self, cluster):
        self.cluster = cluster
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def get_overview(self):
        response = self.session.get(self.mk_endpoint_url("/overview"))
        return response.json() if response.ok else None

    def mk_endpoint_url(self, *endpoint):
        endpoint = "/".join(endpoint)
        return "%s/%s" % (
            self.cluster.get_api_url(),
            endpoint.lstrip("/"),
        )

    def get_vhosts(self):
        response = self.session.get(self.mk_endpoint_url("/vhosts"))
        return response.json() if response.ok else None

    def get_vhost(self, name):
        response = self.session.get(self.mk_endpoint_url("/vhosts", name))
        return response.json() if response.ok else None

    def create_vhost(self, name=None, **kwargs):
        vhost = Vhost(name)
        if self.get_vhost(vhost.name):
            raise Exception("Vhost already exists: %s" % vhost)
        r = self.session.put(self.mk_endpoint_url("vhosts", vhost.name))
        if not r.ok:
            raise Exception(r.text)
        return vhost

    def create_user(self, **kwargs):
        user = User(
            gen_random_string(8, "user"),
            gen_random_string(16),
        )

        tags = kwargs.pop("tags", ["management"])

        salt = os.urandom(4)
        salted_password = salt + user.password.encode("utf-8")
        salted_password_hash = hashlib.sha256(salted_password)
        pwd = salt + salted_password_hash.digest()
        encoded = base64.b64encode(pwd).decode()

        data = dict(
            password_hash=encoded,
            tags=",".join(list(tags)),
        )

        r = self.session.put(
            self.mk_endpoint_url("users", user.user),
            data=json.dumps(data),
        )

        if not r.ok:
            raise Exception(r.text)
        return user

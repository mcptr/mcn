#!/usr/bin/env python

import os
import random
import uuid
import argparse
import json
import pprint
from collections import namedtuple

import mcn.manager
import mcn.manager.argparser


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        add_help=False,
        parents=[mcn.manager.argparser.parser]
    )

    parser.add_argument("name")

    args = parser.parse_args()

    assert(os.path.isfile(args.cluster_config))
    cluster = mcn.manager.Cluster(json.load(open(args.cluster_config, "r")))

    mgr = mcn.manager.RabbitMQManager(cluster)
    user = mgr.create_user(tags=["management"])
    vhost = mgr.create_vhost(args.name)
    # mgr.set_user_permissions(user, vhost, ".*", ".*", ".*")

    sh_env = "\n".join(
        [
            " # sh environment config:",
            "export AMQP_URL='%s'" % cluster.get_amqp_url(
                vhost=vhost, user=user
            )
        ]
    )

    print("".center(72, "-"))
    print("".center(72, " "))
    print(sh_env)
    print("".center(72, " "))
    print("".center(72, "-"))

#!/usr/bin/env python

from mcn.core.storage import connect_mongo

import os
from urllib.parse import urlparse


db = connect_mongo(os.environ["MONGODB_URL"]).get_default_database()
print(db)

records = db.urls.find({"url": {"$regex": "\.gov\.pl\/"}})
domains = set(filter(bool, map(lambda r: (urlparse(r["url"]).hostname or "").strip(), records)))
for d in domains:
    tags = set(set(d.split(".")) - set(["gov", "pl", "www"]))

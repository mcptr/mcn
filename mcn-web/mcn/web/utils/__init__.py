import json
import flask
import bson.objectid
import bson.json_util


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bson.objectid.ObjectId):
            return str(obj)
        else:
            return obj


def jsonify(o):
    return flask.Response(
        response=bson.json_util.dumps(o),
        status=200,
        mimetype="application/json",
    )

import flask
import time


app = flask.Blueprint("url", __name__)


@app.route("/tag")
def tag():
    url = flask.request.args.get("url", None)
    tag = flask.request.args.get("tag", None)

    print(tag, url)

    return flask.jsonify(dict(time=time.time()))

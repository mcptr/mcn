import flask


import apps.home
import apps.feeds
import apps.cache


app = flask.Flask(__name__)

app.register_blueprint(apps.home.app)
app.register_blueprint(apps.feeds.app, url_prefix="/feeds")
app.register_blueprint(apps.cache.app, url_prefix="/cache")


if __name__ == "__main__":
    app.run(debug=True)

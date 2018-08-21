import sys
import logging
import flask

import apps.jinja_filters
import apps.search
import apps.url


LOG_FORMAT = (
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:] %(message)s"
)

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format=LOG_FORMAT,
)


app = flask.Flask(
    __name__,
    static_folder="../static",
)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True

apps.jinja_filters.register(app)


app.register_blueprint(apps.search.app)
app.register_blueprint(apps.url.app, url_prefix="/url")


if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=True,
    )

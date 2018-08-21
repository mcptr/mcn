import flask


app = flask.Blueprint(
    "home",
    __name__,
    template_folder="templates"
)


@app.route("/")
def home():
    return flask.render_template(
        "home/home.html",
    )

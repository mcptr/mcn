import flask
import random
from mcn.web.ui import mk_pagination


app = flask.Blueprint(
    "feeds",
    __name__,
    template_folder="templates"
)


@app.route("/random")
@app.route("/random/page/<int:page_id>")
def random_feed(page_id=1):
    limit = 5
    page_id = (page_id or 1)

    results = [
        dict(
            url=(
                flask.url_for(
                    "feeds.random_feed",
                    page_id=random.randint(0, 10*1000),
                    _external=True,
                )
            )
        ) for i in range(0, limit + 1)
    ]

    return flask.render_template(
        "feeds/listing.html",
        results=results,
        pagination=mk_pagination("feeds.random_feed", results, page_id, limit),
    )

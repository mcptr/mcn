import flask
import datetime

from mcn.searchfeed.search import Search
from mcn.searchfeed.search.providers.bing import BingHTML
from mcn.searchfeed.search.providers.ecosia import EcosiaHTML
from mcn.searchfeed.search.providers.duckduckgo import DuckDuckGoHTML
from mcn.searchfeed.search.providers.mcn.searchfeed import Mcn.Searchfeed
from mcn.searchfeed import processors
import mcn.searchfeed.analysis.search




app = flask.Blueprint("search", __name__)

search_engine = Search(
    # on_result=dump_results,
    providers=[
        # DuckDuckGoHTML(),
        EcosiaHTML(),
        # BingHTML(),
        Mcn.Searchfeed(),
    ],
    before=[
        processors.Group(
            "text",
            [
                processors.Length(),
                processors.word_count,
            ]
        )
    ]
)


@app.route("/")
def search():
    query = flask.request.args.get("q", None)
    start_timer = datetime.datetime.now()
    product = search_engine(query) if query else None
    end_timer = datetime.datetime.now()

    return flask.jsonify(
        dict(
            query=(query or ""),
            results=(product._asdict() if product else None),
            time=(end_timer - start_timer).microseconds

        )
    )


@app.route("/html")
def search_html():
    query = flask.request.args.get("q", None)
    start_timer = datetime.datetime.now()
    product = search_engine(query)  # if query else None
    end_timer = datetime.datetime.now()

    urls = mcn.searchfeed.analysis.search.process(product)

    return flask.render_template(
        "search.html",
        query=(query or ""),
        product=product,
        urls=urls,
        time=(end_timer - start_timer).microseconds
    )

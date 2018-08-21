import flask
from mcn.web import settings
from mcn.web.utils import jsonify
import mcn.core.storage
from bson.objectid import ObjectId


app = flask.Blueprint("cache", __name__)


@app.route("/documents")
@app.route("/documents/<int:page_id>")
def documents_index(page_id=0):
    limit = 10
    mongo_client = mcn.core.storage.connect_mongo(
        settings.MONGODB_URL
    )
    db = mongo_client.mcn.urls
    docs = db.documents.find(
        {}, dict(headers=0, content=0)
    ).skip(page_id * limit).limit(limit)
    return jsonify(docs)


@app.route("/document/<string:document_id>")
def get_document(document_id):
    mongo_client = mcn.core.storage.connect_mongo(
        settings.MONGODB_URL
    )
    db = mongo_client.mcn.urls
    doc = db.documents.find_one(
        dict(_id=document_id)
    )
    return jsonify(doc)

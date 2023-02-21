import requests

from flask import Flask, request, jsonify
import lxml
from readability import Document

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    return "Hello World! Make a request to /api with the input in the \"text\" field to see suggested edits."

@app.route("/", methods=["POST"])
def api():
    """
    Format:
    {
        "utl": "https://www.google.com",
        "html": "<html><body><p>The quick brown fox jumped over the lazy dog.</p></body></html>"",
        "body": "<p>The quick brown fox jumped over the lazy dog.</p>"
    }
    Will figure more out later like credentials.
    """
    obj = request.get_json()
    url = obj["url"]
    html = obj.get("html", requests.get(obj["url"]).text)
    document = Document(html)
    tree = lxml.html.fromstring(document.summary())
    this_level: list[lxml.html] = [tree]
    while this_level:
        next_level = []
        for elem in this_level:
            if elem.tag not in ("figure", "a"):
                elem.attrib.clear()
            next_level.extend(elem)
        this_level = next_level
    text = lxml.html.tostring(tree.body).decode('utf-8').replace("<body>", "").replace("</body>", "")
    result = {
        "url": obj["url"],
        "text": text
    }
    app.logger.info('Page %s simplified successfully', url)
    return jsonify(result)
from flask import Flask, request
import lxml
# from .openai_client import get_edits
import requests
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
    html = obj.get("html", requests.get(obj["url"]).text)
    document = Document(html)
    tree = lxml.html.fromstring(document.summary())
    this_level: list[lxml.html] = [tree]
    while this_level:
        next_level = []
        for elem in this_level:
            print(elem)
            elem.attrib.clear()
            next_level.extend(elem)
        this_level = next_level
    return str(lxml.html.tostring(tree)).replace("<html><body>", "").replace("</body></html>", "")

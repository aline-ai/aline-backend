import requests

from flask import Flask, request, jsonify

from .simplify import simplify
from .autocomplete import autocomplete

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    return "Hello World! Make a request to /api with the input in the \"text\" field to see suggested edits."

@app.route("/simplify", methods=["POST"])
def simplify_api():
    """
    Format:
    {
        "url": "https://www.google.com",
        "html": "<html><body><p>The quick brown fox jumped over the lazy dog.</p></body></html>"",
        "body": "<p>The quick brown fox jumped over the lazy dog.</p>"
    }
    Will figure more out later like credentials.
    """
    obj = request.get_json()
    url = obj["url"]
    html = obj.get("html", requests.get(obj["url"]).text)
    text = simplify(html, obj["title"])
    result = {
        "url": obj["url"],
        "text": text
    }
    app.logger.info('Page %s simplified successfully', url)
    return jsonify(result)

@app.route("/autocomplete", methods=["POST"])
def autocomplete_api():
    """
    Format:
    {
        "url": "https://www.google.com",
        "notes": "<p>This is a note.,</p>",
        "context": "<html><body><p>The quick brown fox jumped over the lazy dog.</p></body></html>"",
    }
    """
    obj = request.get_json()
    url = obj["url"]
    notes = obj["notes"]
    context = obj["context"]
    return jsonify({
        "suggestion": autocomplete(url, context, notes)
    })

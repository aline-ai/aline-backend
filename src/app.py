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
    # document = Document(html)
    # title = document.title()
    # if title == "[no-title]":
    #     title = obj["title"]
    # tree = lxml.html.fromstring(document.summary())
    # this_level: list[lxml.html] = [tree]
    # while this_level:
    #     next_level = []
    #     for elem in this_level:
    #         if elem.tag not in ("figure", "a"):
    #             elem.attrib.clear()
    #         next_level.extend(elem)
    #     this_level = next_level
    # while len(tree) == 1 and tree[0].tag != "p":
    #     tree = tree[0]
    # text = f"<h1>{title}</h1></br>" + "".join([lxml.html.tostring(child).decode('utf-8') for child in tree]).replace("\n", "").replace("\r", "")
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
    # prompt = load_prompt("src/prompts/v1.yaml")
    # completion = openai.Completion.create(
    #     engine="text-davinci-003", 
    #     # engine="text-curie-001", 
    #     prompt = prompt.format(url=url, context=context, notes=notes),
    #     max_tokens=2000,
    #     stop=["===END==="],
    # )
    return jsonify({
        "suggestion": autocomplete(url, context, notes)
    })

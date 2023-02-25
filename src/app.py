import requests

from flask import Flask, request, jsonify
import lxml
from readability import Document
# from langchain.prompts import load_prompt

import openai

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    return "Hello World! Make a request to /api with the input in the \"text\" field to see suggested edits."

@app.route("/simplify", methods=["POST"])
def simplify():
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

prompt = \
"""
Given the context from the article from "{url}" and the notes the user has taken, complete the note:

===START===

{context}

===END===

Complete the following notes a user is taking in HTML:

===START===

{notes}
"""

@app.route("/autocomplete", methods=["POST"])
def autocomplete():
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
    completion = openai.Completion.create(
        engine="text-davinci-003", 
        prompt=prompt.format(url=url, context=context, notes=notes),
        max_tokens=2000
    )
    return jsonify({
        "suggestion": completion.choices[0].text
    })

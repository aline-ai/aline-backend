from flask import Flask, request
from .openai_client import get_edits

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    return "Hello World! Make a request to /api with the input in the \"text\" field to see suggested edits."

@app.route("/", methods=["POST"])
def api():
    req = request.get_json()
    if "text" not in req:
        return "Please provide the input in the \"text\" field.", 400
    text = req["text"]
    n = req.get("n", 1)
    choices = get_edits(text, n=n)
    return [choice.text.strip() for choice in choices if choice["finish_reason"] == "stop"]


import requests

import modal
from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger

from src.simplify import simplify

image = modal.Image.debian_slim().pip_install(
    "openai", 
    "anthropic",
    "markdownify", 
    "mistletoe", 
    "numpy", 
    "langchain", 
    "requests", 
    "readability-lxml", 
    "loguru"
)
web_app = FastAPI()
stub = modal.Stub("api")
stub.store = modal.Function.from_name("s3", "store")
stub.embeddings = modal.Function.from_name("utils", "Embeddings.encode")

@web_app.get("/")
def hello():
    return "Hello World! Make a request to /api with the input in the \"text\" field to see suggested edits."

class SimplifyRequest(BaseModel):
    url: str
    html: str = ""
    title: str

@web_app.post("/simplify")
def simplify_api(request: SimplifyRequest):
    """
    Format:
    {
        "url": "https://www.google.com",
        "html": "<html><body><p>The quick brown fox jumped over the lazy dog.</p></body></html>"",
        "body": "<p>The quick brown fox jumped over the lazy dog.</p>"
    }
    Will figure more out later like credentials.
    """
    url = request.url
    html = request.html or requests.get(url).text
    text = simplify(html, request.title) 
    logger.info('Page %s simplified successfully', url)
    return {"url": url, "text": text}

class AutosuggestRequest(BaseModel):
    url: str
    notes: str = ""
    context: str = ""

@web_app.post("/autocomplete")
def autosuggestion_api(request: AutosuggestRequest):
    """
    Format:
    {
        "url": "https://www.google.com",
        "notes": "<p>This is a note.,</p>",
        "context": "<html><body><p>The quick brown fox jumped over the lazy dog.</p></body></html>"",
    }
    """
    from src.autosuggestion import autosuggestion
    return {"suggestion": autosuggestion(request.url, request.context, request.notes)}


@stub.function(
    image=image, 
    secrets=[modal.Secret.from_name("openai"), modal.Secret.from_name("anthropic")],
)
@stub.asgi_app(label="api")
def fastapi_endpoint():
    return web_app
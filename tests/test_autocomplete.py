from requests import post, get
import logging
from src.simplify import simplify

logger = logging.getLogger(__name__)
format = "%(asctime)s %(clientip)-15s %(user)-8s %(message)s"
logging.basicConfig(format=format, level=logging.INFO)

port = 5000
api_url = f"http://localhost:{port}/"

def test_completion():
    url = "https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04" 
    context = simplify(get(url).text)
    data = post(api_url + "autocomplete", json={
        "url": url,
        "notes": "<p>Definition of transformer</p><ul><li>",
        # "context": "<html><body><p>The quick brown fox jumped over the lazy dog.</p></body></html>"
        "context": context
    }).json()["suggestion"]
    logger.info(data)

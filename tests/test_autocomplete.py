from requests import post
import logging

logger = logging.getLogger(__name__)
format = "%(asctime)s %(clientip)-15s %(user)-8s %(message)s"
logging.basicConfig(format=format, level=logging.INFO)

port = 5000
url = f"http://localhost:{port}/"

def test_completion():
    data = post(url + "autocomplete", json={
        "url": "https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04",
        "notes": "<p>This is a note.,</p>",
        "context": "<html><body><p>The quick brown fox jumped over the lazy dog.</p></body></html>"
    }).json()["suggestion"]
    logger.info(data)

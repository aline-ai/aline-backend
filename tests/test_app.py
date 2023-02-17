from requests import post
import logging

logger = logging.getLogger(__name__)
format = "%(asctime)s %(clientip)-15s %(user)-8s %(message)s"
logging.basicConfig(format=format, level=logging.INFO)

def get_edits_call(endpoint, n = 3):
    data = post(endpoint, json={"text": "Hello everyone my name is Joe.", "n": n}).json()
    assert len(data) == n # could fail due to stop sequence and stuff
    logger.info(data)

def test_heroku():
    get_edits_call("https://rewriter-api.herokuapp.com/")

def test_local(port = 5000):
    get_edits_call(f"http://localhost:{port}/")

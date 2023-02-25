from requests import post
import logging

logger = logging.getLogger(__name__)
format = "%(asctime)s %(clientip)-15s %(user)-8s %(message)s"
logging.basicConfig(format=format, level=logging.INFO)

def test_endpoints(endpoint):
    data = post(endpoint, json={"url": "https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04"}).json()
    logger.info(data)

def test_remote():
    test_endpoints("https://aline-backend-zqvkdcubfa-uw.a.run.app/")

def test_local(port = 5000):
    test_endpoints(f"http://localhost:{port}/")

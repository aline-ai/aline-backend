from requests import post, get
import logging

import pytest
from src.autocomplete import autocomplete

from src.simplify import simplify

logger = logging.getLogger(__name__)
format = "%(asctime)s %(clientip)-15s %(user)-8s %(message)s"

port = 5000
api_url = f"http://localhost:{port}/"
api_url = "https://aline-ai--api-dev.modal.run/"

@pytest.fixture
def article_url():
    return "https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04"

def test_completion_local(article_url):
    context = simplify(get(article_url).text)
    data = autocomplete(article_url, context, "<p>Definition of transformer</p><ul><li>")
    logger.info(data)

def test_completion(article_url):
    context = simplify(get(article_url).text)
    data = post(api_url + "autocomplete", json={
        "url": article_url,
        "notes": "<p>Definition of transformer</p><ul><li>",
        "context": context
    }).json()["suggestion"]
    logger.info(data)

def test_completion_quick(article_url):
    data = post(article_url + "autocomplete", json={
        "url": article_url,
        "notes": "<p>Definition of transformer</p><ul><li>",
        "context": "<h1>What is a Transformer?. An Introduction to Transformers and… | by Maxime | Inside Machine learning | Medium</h1><br><p></p><h1>What is a Transformer?</h1><figure class=\"eu ew if ig ih ii eq er paragraph-image\"></figure><h1>An Introduction to Transformers and Sequence-to-Sequence Learning for Machine Learning</h1><p>New deep learning models are introduced at an increasing rate and sometimes it’s hard to keep track of all the novelties. That said, one particular neural network model has proven to be especially effective for common natural language processing tasks. The model is called a Transformer and it makes use of several methods and mechanisms that I’ll introduce here. The papers I refer to in the post offer a more detailed and quantitative description.</p><h1><strong>Part 1: Sequence to Sequence Learning and Attention</strong></h1><p><a class=\"ae kl\" href=\"https://arxiv.org/abs/1706.03762\" rel=\"noopener ugc nofollow\" target=\"_blank\">The paper</a> ‘Attention Is All You Need’ describes transformers and what is called a sequence-to-sequence architecture. Sequence-to-Sequence (or Seq2Seq) is a neural net that transforms a given sequence of elements, such as the sequence of words in a sentence, into another sequence. (Well, this might not surprise you considering the name.)</p><p>Seq2Seq models are particularly good at translation, where the sequence of words from one language is transformed into a sequence of different words in another language. A popular choice for this type of model is Long-Short-Term-Memory (LSTM)-based models. With sequence-dependent data, the LSTM modules can give meaning to the sequence while remembering (or forgetting) the parts it finds important (or unimportant). Sentences, for example, are sequence-dependent since the order of the words is crucial for understanding the sentence. LSTM are a natural choice for this type of data.</p><p>Seq2Seq models consist of an Encoder and a Decoder. The Encoder takes the input sequence and maps it into a higher dimensional space (n-dimensional vector). That abstract vector is fed into the Decoder which turns it into an output sequence. The output sequence can be in another language, symbols, a copy of the input, etc.</p>"
    }).json()["suggestion"]
    logger.info(data)
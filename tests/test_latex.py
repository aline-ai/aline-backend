import requests
from loguru import logger

def test_simple_latex():
    results = requests.post(
        "https://aline-ai--latex-render.modal.run", 
        json={"latex": open("tests/example.tex").read()}
    )
    logger.info(results)
    with open("tests/example.pdf", "wb") as f:
        f.write(results.content)


def test_markdown_latex():
    results = requests.post(
        "https://aline-ai--latex-render.modal.run", 
        json={"latex": open("tests/markdown.tex").read()}
    )
    logger.info(results)
    with open("tests/markdown.pdf", "wb") as f:
        f.write(results.content)


def test_markdown_endpoint_latex():
    results = requests.post(
        "https://aline-ai--latex-render-markdown.modal.run", 
        json={"markdown": open("tests/example.md").read()}
    )
    logger.info(results)
    with open("tests/markdown_endpoint.pdf", "wb") as f:
        f.write(results.content)


def test_html_endpoint_latex():
    notes_in_html = "<p>Definition of transformer</p><ul><li>"
    results = requests.post(
        "https://aline-ai--latex-render-html.modal.run", 
        json={"html": notes_in_html}
    )
    logger.info(results)
    with open("tests/html_endpoint.pdf", "wb") as f:
        f.write(results.content)

import requests

def test_simple_latex():
    results = requests.post(
        "https://aline-ai--latex-render.modal.run", 
        json={"latex": open("tests/example.tex").read()}
    )
    with open("tests/example.pdf", "wb") as f:
        f.write(results.content)


def test_markdown_latex():
    results = requests.post(
        "https://aline-ai--latex-render.modal.run", 
        json={"latex": open("tests/markdown.tex").read()}
    )
    with open("tests/markdown.pdf", "wb") as f:
        f.write(results.content)

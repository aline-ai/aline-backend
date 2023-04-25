import subprocess

from markdownify import markdownify as md
from pydantic import BaseModel
from fastapi import Response
import modal

image = modal.Image.debian_slim() \
    .apt_install(
        "texlive-latex-base",
        "texlive-latex-extra",
    ) \
    .pip_install(
        "mistletoe", 
        "numpy", 
        "requests", 
        "loguru",
        "markdownify"
    )
stub = modal.Stub("latex")

def create_pdf(file_name):
    process = subprocess.Popen([
        'pdflatex',
        '-output-format=pdf',
        '--shell-escape', # no fucking clue why this breaks without it
        file_name])
    process.wait()

class RenderRequest(BaseModel):
    latex: str

@stub.function(image=image)
@modal.web_endpoint(method="POST")
def render(request: RenderRequest):
    with open("tmp.tex", "w") as f:
        f.write(request.latex)
    create_pdf("tmp.tex")
    headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    return Response(open("tmp.pdf", "rb").read(), headers=headers, media_type='application/pdf')

class RenderMarkdownRequest(BaseModel):
    markdown: str

template = r"""
\documentclass{article}
\usepackage{markdown}
\begin{document}
\begin{markdown}
{{markdown}}
\end{markdown}
\end{document}
"""

@stub.function(image=image)
@modal.web_endpoint(method="POST")
def render_markdown(request: RenderMarkdownRequest):
    latex = template.replace("{{markdown}}", request.markdown)
    return render(RenderRequest(latex=latex))

class RenderHtmlRequest(BaseModel):
    html: str

@stub.function(image=image)
@modal.web_endpoint(method="POST")
def render_html(request: RenderHtmlRequest):
    return render_markdown(RenderMarkdownRequest(markdown=md(request.html)))

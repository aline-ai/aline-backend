import subprocess

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
        "loguru"
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

# @stub.function(image=image)
# @modal.web_endpoint(method="POST")
# def render(markdown: str):
#     pdfl = pdflatex.PDFLaTeX.from_binarystring(, 'out')
#     pdf, log, cp = pdfl.create_pdf()

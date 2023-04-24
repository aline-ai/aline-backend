import markdown
from markdown.extensions import Extension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension

def render_markdown_to_latex(markdown_text):
    extensions = [
        Extension(),
        CodeHiliteExtension(),
        FencedCodeExtension(),
        TableExtension(),
    ]

    md = markdown.Markdown(extensions=extensions)
    latex_output = md.convert(markdown_text)

    return latex_output
from langchain.prompts import load_prompt
from markdownify import markdownify
import mistletoe
import openai

prompt_template = load_prompt("src/prompts/markdown_completion.yaml")
CURSOR_INDICATOR = " CURSOR_INDICATOR "
def autocomplete(url, context, notes):
    context_in_markdown = markdownify(context, heading_style="atx")
    notes_in_markdown = markdownify(notes, heading_style="atx").rstrip()
    prompt = prompt_template.format(url=url, context=context_in_markdown, notes=notes_in_markdown)
    completion = openai.Completion.create(
        engine="text-davinci-003", 
        prompt = prompt,
        max_tokens=4096 - len(prompt),
        stop=["===END==="],
    ).choices[0].text
    # notes = mistune.markdown(notes)
    completed_notes = notes_in_markdown + CURSOR_INDICATOR + completion
    completed_notes_html = mistletoe.markdown(completed_notes).replace("\n", "")
    _notes_user, notes_completion = completed_notes_html.split(CURSOR_INDICATOR.strip())
    return notes_completion.strip()

import html
import asyncio
import time

from markdownify import markdownify
import mistletoe
from loguru import logger
import numpy as np
import anthropic
import modal

from src.prompts.autocomplete_prompts import map_prompt, reduce_prompt
from src.utils import achat, chat, split_markdown

max_length_of_completion = 100
chunk_size = 2048
num_of_chunks = 4

stub = modal.Stub("api")

async def extract(content: str, notes: str) -> str:
    return await achat(map_prompt.format(content=content, notes=notes), temperature=0, max_tokens_to_sample=chunk_size)

def construct_notes(notes: str, summaries: str):
    return chat( 
        reduce_prompt.format(notes=notes.rstrip(), summaries=summaries),
        max_tokens_to_sample=max_length_of_completion,
        temperature = 0.3,
    )

def token_length(text: str):
    return anthropic.count_tokens(text)

CURSOR_INDICATOR = " CURSOR_INDICATOR"
def autosuggestion(url, context, notes):
    # TODO: Deal with case where notes is empty

    # Preprocess
    context_in_md = markdownify(context, heading_style="atx")
    notes_in_md = markdownify(notes, heading_style="atx").rstrip()

    if token_length(context_in_md) > 4096:
        documents = split_markdown(context_in_md, chunk_size=chunk_size)

        logger.info("Fetching embeddings and filtering documents...")
        start = time.time()
        notes_vector, *context_vectors = np.array(stub.app.embeddings.call([notes_in_md] + [document for document in documents]))
        logger.info("Embeddings took {} seconds".format(time.time() - start))
        context_documents = [documents[i] for i in np.argsort(np.linalg.norm(context_vectors - notes_vector, axis=1))[:min(len(documents), num_of_chunks)]]

        logger.info("Summarizing context in parallel...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        gather = asyncio.gather(*[extract(document, notes_in_md) for document in context_documents])
        summaries = "\n".join(loop.run_until_complete(gather))
    else:
        logger.info("Using context directly...")
        summaries = context_in_md

    logger.info("Generating suggestion...")
    suggestion = construct_notes(notes_in_md, summaries)
    logger.info("Done completion")
    stub.app.store.spawn({
        "url": url,
        "context": context,
        "notes": notes,
        "suggestion": suggestion,
        "version": "v0"
    }, f"suggestions/v0/{int(time.time() * 1000)}.json")

    if token_length(suggestion) > int(0.8 * max_length_of_completion): # If stop sequence was reason of termination
        if "\n" in suggestion:
            suggestion = suggestion[:suggestion.rfind("\n")]
    
    if notes_in_md.rstrip().endswith("*") and suggestion.startswith("*"):
        suggestion = suggestion[1:]

    suggestion, *_ = suggestion.split("</notes>")

    # Postprocess the prompt to return output html
    completed_notes = notes_in_md + CURSOR_INDICATOR + suggestion
    completed_notes_html = mistletoe.markdown(completed_notes).replace("\n", "")
    _notes_user, notes_completion = completed_notes_html.split(CURSOR_INDICATOR.strip())
    return html.unescape(notes_completion.strip()).replace("<li>", "<li><p>").replace("</li>", "</p></li>")

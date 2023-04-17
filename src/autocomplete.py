import html
import asyncio
import os

from markdownify import markdownify
import mistletoe
import openai
from loguru import logger
import numpy as np
from langchain.text_splitter import MarkdownTextSplitter
import anthropic

from src.prompts.autocomplete_prompts import map_prompt, reduce_prompt

max_length_of_completion = 100
chunk_size = 1024
num_of_chunks = 5

client = anthropic.Client(os.environ.get('ANTHROPIC_API_KEY'))

def chat(prompt, **kwargs) -> str:
    # switch to anthropic
    return client.completion(
        prompt=prompt,
        stop_sequences = [anthropic.HUMAN_PROMPT, "\n</notes>"],
        model="claude-instant-v1",
        **kwargs
    )["completion"]

async def achat(prompt, **kwargs) -> str:
    return (await client.acompletion(
        prompt=prompt,
        stop_sequences = [anthropic.HUMAN_PROMPT, "\n</notes>"],
        model="claude-instant-v1",
        **kwargs
    ))["completion"]

def embeddings(input, **kwargs) -> str:
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=input,
        **kwargs
    )
    return [np.array(data['embedding']) for data in response['data']]

async def extract(content, notes) -> str:
    return await achat(map_prompt.format(content=content, notes=notes), temperature=0, max_tokens_to_sample=chunk_size)

def construct_notes(notes, summaries):
    return chat( 
        reduce_prompt.format(notes=notes.rstrip(), summaries=summaries),
        max_tokens_to_sample=max_length_of_completion,
        temperature = 0.3,
        # stop_sequence = ["\n</notes>"],
        
    )

def token_length(text: str):
    return anthropic.count_tokens(text)

CURSOR_INDICATOR = " CURSOR_INDICATOR"
def autocomplete(_url, context, notes):
    # TODO: Deal with case where notes is empty

    # Preprocess
    context_in_md = markdownify(context, heading_style="atx")
    notes_in_md = markdownify(notes, heading_style="atx").rstrip()

    if token_length(context_in_md) > 2048:
        text_splitter = MarkdownTextSplitter(chunk_size=chunk_size)
        documents = text_splitter.create_documents([context_in_md])

        logger.info("Fetching embeddings and filtering documents...")
        notes_vector, *context_vectors = np.array(embeddings([notes_in_md] + [document.page_content for document in documents]))
        context_documents = [documents[i] for i in np.argsort(np.linalg.norm(context_vectors - notes_vector, axis=1))[:num_of_chunks]]

        logger.info("Summarizing context in parallel...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        gather = asyncio.gather(*[extract(document.page_content, notes_in_md) for document in context_documents])
        summaries = "\n".join(loop.run_until_complete(gather))
        logger.info(summaries)
    else:
        logger.info("Using context directly...")
        summaries = context_in_md

    logger.info("Generating completion...")
    completion = construct_notes(notes_in_md, summaries)
    logger.info("Done completion")

    if token_length(completion) > int(0.8 * max_length_of_completion): # If stop sequence was reason of termination
        if "\n" in completion:
            completion = completion[:completion.rfind("\n")]
    
    if notes_in_md.rstrip().endswith("*") and completion.startswith("*"):
        completion = completion[1:]

    completion, *_ = completion.split("</notes>")

    # Postprocess the prompt to return output html
    completed_notes = notes_in_md + CURSOR_INDICATOR + completion
    completed_notes_html = mistletoe.markdown(completed_notes).replace("\n", "")
    _notes_user, notes_completion = completed_notes_html.split(CURSOR_INDICATOR.strip())
    return html.unescape(notes_completion.strip()).replace("<li>", "<li><p>").replace("</li>", "</p></li>")

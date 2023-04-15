import html

import asyncio
from textwrap import dedent
from markdownify import markdownify
import mistletoe
import openai
from loguru import logger
import numpy as np
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import MarkdownTextSplitter
import tiktoken

max_length_of_completion = 100
chunk_size = 1024
num_of_chunks = 8

def chat(messages, **kwargs) -> str:
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        **kwargs
    ).choices[0].message.content

async def achat(messages, **kwargs) -> str:
    return (await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=messages,
        **kwargs
    )).choices[0].message.content

def embeddings(input, **kwargs) -> str:
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=input,
        **kwargs
    )
    return [np.array(data['embedding']) for data in response['data']]

async def extract(content, notes) -> str:
    return await achat([
        {"role": "system", "content": "Use the following portion of a long article to see if any of the text is relevant complete the incomplete notes. COPY any relevant text VERBATIM, meaning word-for-word."},
        {"role": "user", "content": dedent(f"""
            <article>
            {content}
            </article>

            <notes>
            {notes}
            </notes>
            Relevant text verbatim, if any:
        """)},
    ], temperature=0)

def construct_notes(notes, summaries):
    return chat([
        {
            "role": "system", 
            "content": dedent(f"""
                <summaries>
                {summaries}
                </summaries>

                The following are a small section of notes written according to the following:
                * The notes are based on the context, *not* on prior knowledge
                    * An answer will *not* be written if the answer is not found in the long article
                    * Nothing will be written if nothing is relevant
                * The notes start at the start token (===START===) and end at the end token (===END===)
                * Github-style markdown syntax will be used to format the notes
                    * Lists, which start with astericks (*) will be used dominantly to organize the notes
                    * Indents will be used to nest lists
                    * Headers, which start with hashes (#) will be used SPARINGLY to organize the notes
                * The notes will be elaborate and detailed, but will not generate new section headers
                * Each line will be kept short, simple and concise, and will not exceed 80 characters
                * Multiple clauses or sentences will ALWAYS be broken into multiple lines 
                * Only the next section of notes will be completed

                <notes>
                {notes}
            """)
        }], 
        max_tokens = max_length_of_completion,
        temperature = 0.3,
        # stop_sequence = ["\n</notes>"],
    )


encoding = tiktoken.get_encoding("cl100k_base")

CURSOR_INDICATOR = " CURSOR_INDICATOR"
def autocomplete(_url, context, notes):
    # TODO: Deal with case where notes is empty

    # Preprocess
    context_in_md = markdownify(context, heading_style="atx")
    notes_in_md = markdownify(notes, heading_style="atx").rstrip()

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
    logger.info(f"Summaries: {summaries}")

    logger.info("Generating completion...")
    completion = construct_notes(notes_in_md, summaries)
    if len(encoding.encode(completion)) > int(0.8 * max_length_of_completion): # If stop sequence was reason of termination
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

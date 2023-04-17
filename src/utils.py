import os

import numpy as np
from langchain.text_splitter import MarkdownTextSplitter
import anthropic
import openai

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

def split_markdown(text: str, chunk_size=1024) -> str:
    text_splitter = MarkdownTextSplitter(chunk_size=chunk_size, length_function=anthropic.count_tokens)
    return [document.page_content for document in text_splitter.create_documents([text])]

from typing import Any, Iterable
from markdownify import markdownify
import mistletoe
import html

from langchain.embeddings.openai import OpenAIEmbeddings, Embeddings
from langchain.vectorstores import Chroma,  VectorStore
from langchain.chains import VectorDBQA
from langchain.llms import OpenAI, OpenAIChat
from langchain.chat_models import ChatOpenAI
from langchain.prompts import load_prompt
from langchain.text_splitter import MarkdownTextSplitter

import openai

from dotenv import load_dotenv
import tiktoken

load_dotenv() 

Document = Any

encoding = tiktoken.get_encoding("cl100k_base")

CURSOR_INDICATOR = " CURSOR_INDICATOR"
def autocomplete(_url, context, notes):
    # TODO: Deal with case where notes is empty

    # Preprocess
    context_in_md = markdownify(context, heading_style="atx")
    notes_in_md = markdownify(notes, heading_style="atx").rstrip()

    text_splitter = MarkdownTextSplitter(chunk_size=2048)
    documents = text_splitter.create_documents([context_in_md])
    
    # llm = OpenAIChat(max_tokens=128, verbose=True)
    llm = ChatOpenAI(max_tokens=128, verbose=True)

    # set up streaming to cancel at a certain point
    if len(documents) > 4:
        # Refactor this mess
        embeddings = OpenAIEmbeddings()
        # TODO: Use Qdrant or something that doesn't require like an hour to build
        docsearch = Chroma.from_documents(documents, embeddings)
        qa = VectorDBQA.from_chain_type(
            # llm=OpenAI(max_tokens=2048, verbose=True), # Make this also chat or fine-tune curie to do this
            llm=ChatOpenAI(max_tokens=2048, verbose=True), # Make this also chat or fine-tune curie to do this
            chain_type="map_reduce", 
            vectorstore=docsearch, 
            return_source_documents=True,
        )
        qa.combine_documents_chain.combine_document_chain.llm_chain.llm = llm
        qa.combine_documents_chain.combine_document_chain.llm_chain.llm.model_kwargs = {"stop": ["===END==="]}
        qa.combine_documents_chain.llm_chain.prompt = load_prompt("src/prompts/autocomplete/map.yaml")
        qa.combine_documents_chain.combine_document_chain.llm_chain.prompt = load_prompt("src/prompts/autocomplete/reduce.yaml")
        completion: str = qa({"query": notes_in_md})["result"]
    else:
        prompt = load_prompt("src/prompts/autocomplete/reduce.yaml")
        completion = llm(prompt.format(question=notes_in_md, summaries=context_in_md))
    
    if len(encoding.encode(completion)) > 100: # If stop sequence was reason of termination
        if "\n" in completion:
            completion = completion[:completion.rfind("\n")]
    
    if notes_in_md.rstrip().endswith("*") and completion.startswith("*"):
        completion = completion[1:]

    completion, *_ = completion.split("===END===")

    # Postprocess the prompt to return output html
    completed_notes = notes_in_md + CURSOR_INDICATOR + completion
    completed_notes_html = mistletoe.markdown(completed_notes).replace("\n", "")
    _notes_user, notes_completion = completed_notes_html.split(CURSOR_INDICATOR.strip())
    return html.unescape(notes_completion.strip()).replace("<li>", "<li><p>").replace("</li>", "</p></li>")

if __name__ == "__main__":
    chat = ChatOpenAI()
    embeddings = OpenAIEmbeddings()
    

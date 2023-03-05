from langchain.prompts import load_prompt
from markdownify import markdownify
import mistletoe

import requests

from markdownify import markdownify as md

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQA
from langchain.llms import OpenAI, OpenAIChat
from langchain.prompts import load_prompt
# from langchain.indexes import VectorstoreIndexCreator
from langchain import PromptTemplate
from langchain.text_splitter import MarkdownTextSplitter

from readability import Document
import lxml

# prompt_template = load_prompt("src/prompts/markdown_completion.yaml")
# CURSOR_INDICATOR = " CURSOR_INDICATOR "
# def autocomplete(url, context, notes):
#     context_in_markdown = markdownify(context, heading_style="atx")
#     notes_in_markdown = markdownify(notes, heading_style="atx").rstrip()
#     prompt = prompt_template.format(url=url, context=context_in_markdown, notes=notes_in_markdown)
#     completion = openai.Completion.create(
#         engine="text-davinci-003", 
#         prompt = prompt,
#         max_tokens=4096 - len(prompt),
#         stop=["===END==="],
#     ).choices[0].text
#     # notes = mistune.markdown(notes)
#     completed_notes = notes_in_markdown + CURSOR_INDICATOR + completion
#     completed_notes_html = mistletoe.markdown(completed_notes).replace("\n", "")
#     _notes_user, notes_completion = completed_notes_html.split(CURSOR_INDICATOR.strip())
#     return notes_completion.strip()

CURSOR_INDICATOR = " CURSOR_INDICATOR"
def autocomplete(_url, context, notes):
    # TODO: Deal with case where notes is empty

    # Preprocess
    context_in_md = markdownify(context, heading_style="atx")
    notes_in_md = markdownify(notes, heading_style="atx").rstrip()
    # prompt = prompt_template.format(url=url, context=context_in_markdown, notes=notes_in_markdown)

    text_splitter = MarkdownTextSplitter()
    documents = text_splitter.create_documents([context_in_md])

    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_documents(documents, embeddings)
    # index = VectorstoreIndexCreator().from_loaders([context_in_md])
    qa = VectorDBQA.from_chain_type(
    llm=OpenAI(
        max_tokens=1024, 
        verbose=True
    ), 
    chain_type="map_reduce", 
    vectorstore=docsearch, 
    return_source_documents=True
    )
    # qa.verbose = True
    # qa.combine_documents_chain.verbose = True
    # qa.combine_documents_chain.llm_chain.verbose = True
    # qa.combine_documents_chain.combine_document_chain.llm_chain.verbose = True
    # qa.combine_documents_chain.llm_chain.llm.model_name = "text-curie-001"
    qa.combine_documents_chain.combine_document_chain.llm_chain.llm = OpenAIChat(max_tokens=1024, verbose=True)
    qa.combine_documents_chain.combine_document_chain.llm_chain.llm.model_kwargs = {"stop": ["===END==="]}
    qa.combine_documents_chain.llm_chain.prompt = load_prompt("src/prompts/autocomplete/map.yaml")
    qa.combine_documents_chain.combine_document_chain.llm_chain.prompt = load_prompt("src/prompts/autocomplete/reduce.yaml")


    completion = qa({"query": notes})["result"]

    # Postprocess the prompt to remove the cursor indicator
    # notes = mistune.markdown(notes)
    completed_notes = notes_in_md + CURSOR_INDICATOR + completion
    completed_notes_html = mistletoe.markdown(completed_notes).replace("\n", "")
    _notes_user, notes_completion = completed_notes_html.split(CURSOR_INDICATOR.strip())
    return notes_completion.strip()
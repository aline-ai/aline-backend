from markdownify import markdownify
import mistletoe

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQA
from langchain.llms import OpenAI, OpenAIChat
from langchain.prompts import load_prompt
from langchain.text_splitter import MarkdownTextSplitter

CURSOR_INDICATOR = " CURSOR_INDICATOR"
def autocomplete(_url, context, notes):
    # TODO: Deal with case where notes is empty

    # Preprocess
    context_in_md = markdownify(context, heading_style="atx")
    notes_in_md = markdownify(notes, heading_style="atx").rstrip()

    text_splitter = MarkdownTextSplitter()
    documents = text_splitter.create_documents([context_in_md])

    # Refactor this mess
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_documents(documents, embeddings)
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

    # Postprocess the prompt to return output html
    completed_notes = notes_in_md + CURSOR_INDICATOR + completion
    completed_notes_html = mistletoe.markdown(completed_notes).replace("\n", "")
    _notes_user, notes_completion = completed_notes_html.split(CURSOR_INDICATOR.strip())
    return notes_completion.strip()
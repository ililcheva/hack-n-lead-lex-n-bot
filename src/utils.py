import os
import yaml
import argparse

from langchain import OpenAI, PromptTemplate
from langchain.chains import ConversationalRetrievalChain

from prompts import SYSTEM_MESSAGE, CONVERSATION_MESSAGE_STRUCTURE

def load_config():
    filepath = os.path.abspath("../config.yml")
    with open(filepath, 'r') as file:
        yaml_dict = yaml.safe_load(file)

    return yaml_dict


def parse_args(args):
    parser = argparse.ArgumentParser('Lexi')
    parser.add_argument('--api_key', help='OpenAI API Key', required=True)
    parser.add_argument('--org', help='OpenAI Organization', required=True)
    return parser.parse_args(args)


def create_sources(documents):
    sources = {
        document.metadata['url']: {'topic': document.metadata['title'], 'title': document.metadata['url']} for document in documents}
    return "|".join([f" [{metadata['topic']}]({topic}) " for topic, metadata in sources.items()])


def create_chain(memory, model_name, api_key, identity, retrievers, top_k_documents=3, collection_name='swiss-law'):
    system_message = SYSTEM_MESSAGE.format(identity)
    conversation_structure_message = CONVERSATION_MESSAGE_STRUCTURE
    template = system_message + conversation_structure_message

    llm = OpenAI(
        model_name=model_name,
        openai_api_key=api_key,
        temperature=0)

    qa_prompt = PromptTemplate(input_variables=['chat_history', 'question', 'context'], template=template)
    retriever = retrievers[collection_name].as_retriever(search_kwargs={'k': top_k_documents})
    chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={'prompt': qa_prompt},
        verbose=True
    )
    chain.return_source_documents=True
    return chain
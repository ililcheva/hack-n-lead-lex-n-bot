import sys
import openai
import argparse
import streamlit as st

from qdrant_client import QdrantClient, models
from langchain.callbacks import StreamlitCallbackHandler
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.vectorstores import Qdrant

from utils import (create_sources, create_chain, load_config, parse_args)
from prompts import IDENTITY, INITIAL_AI_MESSAGE

config = load_config()
api_key = parse_args(sys.argv[1:]).api_key
org = parse_args(sys.argv[1:]).org

client = QdrantClient(host=config['db']['host'], port=config['db']['port'])

vector_params = models.VectorParams(
    size=config['vector_size'],
    distance=models.Distance.COSINE
)

openai.api_key = api_key
openai.api_base = config['open_ai_url']

embeddings_model = OpenAIEmbeddings(
    model=config['embeddings_model_name'],
    openai_api_key=api_key,
    openai_organization=org,
    openai_api_base=config['open_ai_url']
)

retrievers = {
    name: Qdrant(client, collection_name=name, embeddings=embeddings_model) for name in config['collections']
}

st.set_page_config(page_title=config['title'], layout='wide')

msgs = StreamlitChatMessageHistory()

memory = ConversationBufferMemory(memory_key='chat_history', chat_memory=msgs, return_messages=True, output_key='answer')

if len(msgs.messages) == 0:
    msgs.add_ai_message(INITIAL_AI_MESSAGE)

for msg in msgs.messages:
    content = msg.content
    print(content)
    if 'source' in msg.additional_kwargs:
        content += msg.additional_kwargs['source']
    st.chat_message(config['avatars'][msg.type]).write(content)


if prompt := st.chat_input('Tell me what you want to find'):

    with st.chat_message(config['avatars']['human']):
        st.markdown(prompt)

    with st.chat_message(config['avatars']['ai']):

        container = st.container()
        st_callback = StreamlitCallbackHandler(container)
        llm_chain = create_chain(
            memory, config['model_name'], api_key, IDENTITY, 
            retrievers, top_k_documents=config['top_k_documents'], collection_name=config['collections'][0])
        response=llm_chain({"question": prompt}, callbacks=[st_callback])
        st_callback._complete_current_thought("Completed")

        source = "\n\nSources:" + create_sources(documents=response['source_documents'])
        response['answer'] += source

        msgs.messages[-1].additional_kwargs['source'] = source

        container.markdown(response['answer'])

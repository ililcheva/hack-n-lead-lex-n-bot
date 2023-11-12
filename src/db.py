import sys
import openai

from datasets import load_dataset
from qdrant_client import QdrantClient, models
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.schema.document import Document

from utils import load_config

config = load_config()
api_key = sys.argv[1]
collection_name = config['collections'][0]

openai.api_key = api_key
openai.api_base = config['open_ai_url']

embeddings_model = OpenAIEmbeddings(
    model=config['embeddings_model_name'],
    openai_api_key=api_key,
    openai_organization = config['open_ai_organization'],
    openai_api_base=config['open_ai_url']
)

client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)

vector_params = models.VectorParams(
    size=config['vector_size'],
    distance=models.Distance.COSINE
)

client.create_collection(
    collection_name=collection_name,
    vectors_config=vector_params,
)

vectorstore = Qdrant(client, collection_name=collection_name, embeddings=embeddings_model)

dataset = load_dataset(config['dataset']['name'])[config['dataset']['collection']]
df = dataset.to_pandas()
df = df.drop(columns=["vector", "headings"])
df_dict = df.to_dict('records')

docs = []
for row in df_dict:
    document_article = Document(page_content=str(row['content']))
    document_article.metadata.update(title=row['article'], url=row['link'])
    docs.append(document_article)

vectorstore.add_documents(docs)
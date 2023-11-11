import openai

from datasets import load_dataset
from qdrant_client import QdrantClient, models
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.schema.document import Document


api_key = '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'
url = 'https://api.openai.com/v1/'
embedding_name = 'text-embedding-ada-002'
size = 1536

collection_name = 'swiss-law'

openai.api_key = api_key
openai.api_base = url

embeddings_model = OpenAIEmbeddings(
    model=embedding_name,
    openai_api_key=api_key,
    openai_organization = 'org-66N72mGO3XwF80FfTwkYtkqT',
    openai_api_base=url
)

client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)

vector_params = models.VectorParams(
    size=size,
    distance=models.Distance.COSINE
)

client.create_collection(
    collection_name=collection_name,
    vectors_config=vector_params,
)


vectorstore = Qdrant(client, collection_name=collection_name, embeddings=embeddings_model)


dataset = load_dataset("brunnolou/swiss-code-of-obligations")['code_of_obligations_en_paraphrase_multilingual']
df = dataset.to_pandas()
docs = []


for article in df['article'].unique().tolist():
    title = str(df.loc[df['article'] == article, 'article'].tolist()[0])
    url = str(df.loc[df['article'] == article, 'link'].tolist()[0])
    content = str(df.loc[df['article'] == article, 'content'].tolist()[0])
    document_article = Document(page_content=content)
    document_article.metadata.update(title=title, url=url)
    docs.append(document_article)

vectorstore.add_documents(docs)
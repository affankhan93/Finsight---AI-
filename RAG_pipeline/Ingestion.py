from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')
import os
import time 

load_dotenv() 

# loading pdfs data
DATA_PATH = "data/financial_data/"
def load_pdfs(data_load):
    loader = PyPDFDirectoryLoader(data_load)
    documents = loader.load()
    return documents

documents = load_pdfs(DATA_PATH)
print(f"Total number of documents are:- {len(documents)}")


# creating chunks of documents 
def create_chunks(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 400, chunk_overlap = 100)
    all_splittes = text_splitter.split_documents(extracted_data)
    return all_splittes

chunks = create_chunks(extracted_data=documents)


# creating vector embeddings
MODEL = 'llama-text-embed-v2'
def vector_embeddings():
    embedding = PineconeEmbeddings(model = MODEL)
    return embedding

embeddings = vector_embeddings()


# Manually build Vector database(Pinecone)
INDEX_NAME = 'financial'
pc = Pinecone(api_key= os.getenv("PINECONE_API_KEY"))
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name = INDEX_NAME,
        dimension=1024,
        metric='cosine', 
        spec = ServerlessSpec(cloud='aws', region='us-east-1')
    )
    time.sleep(10)

vector_store = PineconeVectorStore(index=pc.Index(INDEX_NAME), embedding=embeddings)


# Uploading in small batches with a pause after each one because it throw rate limit error
BATCH_SIZE = 100 
WAIT_SECONDS = 10 
for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i: i + BATCH_SIZE]
    ids = [f"chunks:-{i + j}" for j in range(len(batch))]
    vector_store.add_documents(batch, ids = ids)
    print(f"Uploaded {min(i + BATCH_SIZE, len(chunks))} / {len(chunks)}")
    time.sleep(WAIT_SECONDS)

print("Vector database is created!")
print(pc.Index(INDEX_NAME).describe_index_stats())





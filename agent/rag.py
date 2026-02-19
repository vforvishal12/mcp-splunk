from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def build_vector_db():
    loader = TextLoader("data/runbooks.txt")
    docs = loader.load()

    vectordb = Chroma.from_documents(
        docs,
        embedding,
        persist_directory="./chroma_db"
    )
    vectordb.persist()

def search_docs(query):
    vectordb = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embedding
    )
    return vectordb.similarity_search(query, k=2)

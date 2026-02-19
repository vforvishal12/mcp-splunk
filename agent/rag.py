from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings

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

    docs = vectordb.similarity_search(query, k=2)
    return [d.page_content for d in docs]

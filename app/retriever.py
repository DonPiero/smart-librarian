from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.schema import Document
from pathlib import Path
from typing import List

load_dotenv()

CHROMA_PATH = Path("../data/chroma_store")

#embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    embedding_function=embedding_model,
    persist_directory=str(CHROMA_PATH)
)

def search_books(inquiry: str, matches: int = 3) -> List[Document]:
    return vectorstore.similarity_search(inquiry, k=matches)


from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.schema import Document
from typing import List
import json
from app.config.constants import CHROMA_PATH, DATA_PATH

load_dotenv()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

if CHROMA_PATH.exists() and any(CHROMA_PATH.iterdir()):
    vectorstore = Chroma(
        embedding_function=embedding_model,
        persist_directory=str(CHROMA_PATH)
    )
else:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        books = json.load(f)

    docs = [
        Document(page_content=book["summary"], metadata={"title": book["title"]})
        for book in books
    ]

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=str(CHROMA_PATH)
    )

def search_books(inquiry: str, matches: int = 5) -> List[Document]:
    return vectorstore.similarity_search(inquiry, k=matches)


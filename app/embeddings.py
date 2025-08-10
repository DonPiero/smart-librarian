from pathlib import Path
import json
from langchain_community.vectorstores import Chroma
#from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = Path("../data/book_summaries.json")
CHROMA_PATH = Path("../data/chroma_store")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    books = json.load(f)

docs = []
for book in books:
    doc = Document(
        page_content=book["summary"],
        metadata={"title": book["title"]}
    )
    docs.append(doc)

#embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    persist_directory=str(CHROMA_PATH)
)


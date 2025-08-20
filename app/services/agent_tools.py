import json
from langchain_core.tools import tool
from app.config.constants import DATA_PATH
from app.utils.retriever import search_books

@tool
def get_summary_by_title(title: str) -> str:
    """
        Return the full summary of a book based on its exact title.
        Example: get_summary_by_title("The Hobbit") will return the full summary of "The Hobbit".
    """
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            books = json.load(f)

        for book in books:
            if book["title"].strip().lower() == title.strip().lower():
                return book["full_summary"]

        return f"There is no book entitled: '{title}'."

    except Exception as e:
        return f"We have encountered this error: {e}"

@tool
def search_relevant_books(query: str) -> str:
    """
        Search the library's book collection for relevant books by genre, theme, or topic.
        Returns a string with unique book titles in order.
    """
    matches = search_books(query, matches=5)

    if not matches:
        return ""

    seen = set()
    results = []
    for doc in matches:
        title = doc.metadata.get("title", "").strip()
        if title and title not in seen:
            seen.add(title)
            results.append(title)

    return "\n".join(results)
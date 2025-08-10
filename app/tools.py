import json
from pathlib import Path
from langchain_core.tools import tool

DATA_PATH = Path("../data/book_summaries.json")

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

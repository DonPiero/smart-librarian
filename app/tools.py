import json
from retriever import search_books
from pathlib import Path
from langchain_core.tools import tool

DATA_PATH = Path("../data/book_summaries.json")

def language_filter(text: str) -> bool:
    text = text.lower()
    words = text.split()

    forbidden_words = [
        "prost", "proasta", "idiot", "idiota", "cretin", "cretina", "nebun", "nebuna",
        "bou", "vacă", "dobitoc", "dobitocă", "tâmpit", "tâmpită", "jegos", "scârbă",
        "pula", "muie", "mata", "cur", "fut", "futut", "futai", "dracu", "dracului", "cacat",
        "mortii", "mortu", "mortu-tii", "mortii-mătii", "sugi", "sugeti", "pulă", "panarama",
        "zdreanță", "javră", "ho", "paștele", "sângele", "căcat", "mă-ta", "sugi-o", "fuck",
        "fucked", "fucker", "fucking", "shit", "shitty", "bullshit", "bitch", "bastard",
        "asshole", "dick", "piss", "cunt", "slut", "whore", "moron", "retard", "dumb", "stupid",
        "idiot", "suck", "sucks", "jerk", "freak", "scum", "crap", "loser", "numbnuts", "twat",
        "motherfucker", "son of a bitch", "dumbass"
    ]

    for word in words:
        clean_word = word.strip(".,!?")
        if clean_word in forbidden_words:
            return True
    return False

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
        Search the library's book collection for the most relevant book.
        Returns a string with title and summary.
    """
    matches = search_books(query, matches=3)

    if not matches:
        return "No relevant books were found in the collection."

    return "\n\n".join([
        f"Title: {doc.metadata['title']}\nSummary: {doc.page_content}"
        for doc in matches
    ])
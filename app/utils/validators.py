from app.config.constants import FORBIDDEN_WORDS


def language_filter(text: str) -> bool:
    text = text.lower()
    words = text.split()

    for word in words:
        clean_word = word.strip(".,!?")
        if clean_word in FORBIDDEN_WORDS:
            return True
    return False

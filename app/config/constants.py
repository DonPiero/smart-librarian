import os
from pathlib import Path
from app.config.classes import ModelConfig, PromptConfig

SECRET_KEY = os.getenv("SECRET_KEY", "secret_key_placeholder")
ALGORITHM = "HS256"
DATABASE_URL = "sqlite:///./logs.db"
MODEL_CONFIG = ModelConfig()
PROMPT_CONFIG = PromptConfig()
DATA_PATH = (Path(__file__).resolve()
             .parents[2]
             / "data"
             / "book_summaries.json")
CHROMA_PATH = (Path(__file__).resolve()
               .parents[2]
               / "data"
               / "chroma_store")
FORBIDDEN_WORDS = [
    "prost", "proasta", "idiot", "idioata", "cretin", "cretina", "nebun",
    "nebuna", "bou", "vacă", "dobitoc", "dobitocă", "tâmpit", "tâmpită",
    "jegos", "scârbă", "pula", "muie", "mata", "cur", "fut", "futut",
    "futai", "dracu", "dracului", "cacat", "mortii", "mortu", "mortu-tii",
    "mortii-mătii", "sugi", "sugeti", "pulă", "panarama", "zdreanță",
    "javră", "ho", "paștele", "sângele", "căcat", "mă-ta", "sugi-o", "fuck",
    "fucked", "fucker", "fucking", "shit", "shitty", "bullshit", "bitch",
    "bastard", "asshole", "dick", "piss", "cunt", "slut", "whore", "moron",
    "retard", "dumb", "stupid", "idiot", "suck", "sucks", "jerk", "freak",
    "scum", "crap", "loser", "numbnuts", "twat", "motherfucker",
    "son of a bitch", "dumbass"
]

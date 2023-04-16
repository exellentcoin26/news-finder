from enum import Enum
from typing import Dict, List


class Language(str, Enum):
    English = "english"
    Dutch = "dutch"


def load_stop_words(language: str) -> List[str]:
    with open(f"res/stopwords/{language}.txt", "r") as stop_words:
        return stop_words.read().splitlines()


stop_words: Dict[Language, List[str]] = {
    language: load_stop_words(language) for language in Language
}


def filter_stop_words(text: List[str], language: Language) -> List[str]:
    return [word for word in text if word not in stop_words[language]]


def filter_numerics(text: List[str]) -> List[str]:
    return [word for word in text if not word.isdigit()]

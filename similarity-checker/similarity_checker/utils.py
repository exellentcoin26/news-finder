from typing import Dict, List

import os

from prisma.enums import Language


def language_to_string(language: Language) -> str:
    return {Language.English: "english", Language.Dutch: "dutch"}[language]


def load_stop_words(language: Language) -> List[str]:
    with open(
        os.path.abspath(f"./res/stopwords/{language_to_string(language)}.txt"), "r"
    ) as stop_words:
        return stop_words.read().splitlines()


stop_words: Dict[Language, List[str]] = {
    language: load_stop_words(language) for language in Language
}


def filter_stop_words(text: List[str], language: Language) -> List[str]:
    return [word for word in text if word not in stop_words[language]]


def filter_numerics(text: List[str]) -> List[str]:
    return [word for word in text if not word.isdigit()]

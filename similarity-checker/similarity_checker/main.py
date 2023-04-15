#! /usr/bin/env python3


import asyncio
import os
import re
import math
import string

from typing import List, Dict, Tuple

# TODO: check language of the article
# TODO: Remove stop words from language if dataset is present


async def main():
    articles: List[str] = []

    for article in os.listdir("articles"):
        with open(f"articles/{article}", "r") as article:
            # Remove unnecessary whitespace, punctuation and convert to lowercase
            articles.append(
                re.sub(r"\s+", " ", article.read()).translate(
                    str.maketrans("", "", string.punctuation)
                ).lower()
            )

    print("============================")
    print("Article list:")
    for article in articles:
        print(article)
    print("============================")

    calc_tf_idf(articles)


def calc_tf_idf(documents: List[str]) -> Dict[str, Tuple[List[float], float]]:
    # Join all frequency values in a single table
    tf_table: Dict[str, List[float]] = {}
    for document in documents:
        tf = calc_norm_term_freq(document)

        for [term, freq] in tf.items():
            # Create or insert if present
            tf_table[term] = [*tf_table.get(term, []), freq]

    idf_table = calc_idf(list(tf_table.keys()), documents)
    tf_idf_table = {
        term: (freq, idf_table.get(term, 0)) for [term, freq] in tf_table.items()
    }

    for entry in tf_idf_table.items():
        print(entry)

    return tf_idf_table


def calc_norm_term_freq(document: str) -> Dict[str, float]:
    tf_table: Dict[str, float] = {}
    total_count = 0

    # Count terms occurrences in document
    for term in document.split(" "):
        tf_table[term] = tf_table.get(term, 0) + 1
        total_count += 1

    # Normalize counts
    for term in tf_table.keys():
        tf_table[term] /= total_count

    return tf_table


def calc_idf(terms: List[str], documents: List[str]) -> Dict[str, float]:
    idf_table: Dict[str, float] = {}

    # Count term occurrence over documents
    for term in terms:
        for document in documents:
            if document.find(term) != -1:
                idf_table[term] = idf_table.get(term, 0) + 1

    # Normalize counts
    for term in idf_table.keys():
        idf_table[term] = math.log(len(documents) / idf_table[term], 2)

    return idf_table


def cos_similarity():
    pass


if __name__ == "__main__":
    asyncio.run(main(), debug=True)

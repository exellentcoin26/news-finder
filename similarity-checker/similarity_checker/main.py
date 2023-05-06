#! /usr/bin/env python3


import asyncio

import sys
import re
import math
import string
from datetime import datetime
from typing import List, Dict, Tuple, Set

import schedule
from prisma.models import NewsArticles
from prisma import Prisma

import numpy as np
from numpy.typing import NDArray

from utils import Language, filter_stop_words, filter_numerics

THRESHOLD = 0.50

# failsafe for running async call with non async scheduler.
# Note: this fails if the schedule timestep is lower than the starting of the thread
# (which _should_ never happen).
is_running = False

# TODO: check language of the article


async def main():
    schedule.every(2).seconds.do(run)  # type: ignore

    while True:
        schedule.run_pending()
        next_run = schedule.next_run()
        if next_run is None:
            exit(0)

        delta = next_run - datetime.now()

        print(
            f"Time until next run: {int(delta.total_seconds())} seconds",
            file=sys.stderr,
        )
        await asyncio.sleep(3)


def run():
    asyncio.get_event_loop().create_task(run_similarity_checker())


async def run_similarity_checker():
    global is_running

    if is_running:
        print("Not running checker because last run has not finished", file=sys.stderr)
        return

    is_running = True

    db = Prisma()
    await db.connect()

    raw_articles = await db.newsarticles.find_many(include={"source": True})

    await calc_article_similarity(raw_articles, db)

    await db.disconnect()

    is_running = False


async def calc_article_similarity(
    databse_articles: List[NewsArticles], client: Prisma
) -> Dict[int, Set[int]]:
    """
    Calculates the similarity between articles using tf-idf to vectorize text and uses
    cosine similarity.

    Due to performance reasons (for 1000 articles it takes about 15 minutes) it inserts
    the similar markers immediately into the database.
    """

    raw_articles: List[str] = [
        article.title + (article.description or "") for article in databse_articles
    ]

    print(
        f"Starting similarity checker on list of `{len(raw_articles)}` articles.",
        file=sys.stderr,
    )

    # Remove whitespace, punctuation and convert to lowercase
    cleaned_articles: List[str] = [
        re.sub(r"\s+", " ", article)
        .translate(str.maketrans("", "", string.punctuation))
        .lower()
        for article in raw_articles
    ]
    # Split articles by whitespace and remove stopwords
    articles = [article.split() for article in cleaned_articles]
    articles = [filter_numerics(article) for article in articles]
    # TODO: Get language from database.
    articles = [filter_stop_words(article, Language.English) for article in articles]

    tf_idf_table = calc_tf_idf(articles)

    similar: Dict[int, Set[int]] = {}

    cosine_similarity_table = np.matmul(tf_idf_table, tf_idf_table.T)

    # Check every article against every other article
    print("Checking cosine similarities...", file=sys.stderr)
    for lhs_article_idx in range(len(articles)):
        for rhs_article_idx in range(lhs_article_idx + 1, len(articles)):
            article1, article2 = (
                databse_articles[lhs_article_idx],
                databse_articles[rhs_article_idx],
            )
            assert article1.source is not None and article2.source is not None

            similarity = cosine_similarity_table[lhs_article_idx][rhs_article_idx]
            sys.stdout.write(
                "\033[K"
                + f"Article `{lhs_article_idx}` == Article `{rhs_article_idx}`: {similarity}".expandtabs(
                    2
                )
                + "\r"
            )
            if similarity > THRESHOLD:
                if article1.source.id == article2.source.id:
                    print(
                        f"Found a possible update! ({article1.source.name})",
                        file=sys.stderr,
                    )

                print(
                    "\033[K"
                    + f"Found:\n\t`{' '.join(articles[lhs_article_idx])}`\n"
                    + "\t"
                    + article1.source.name
                    + "\n\t=="
                    + f"\n\t`{' '.join(articles[rhs_article_idx])}\n"
                    + "\t"
                    + article2.source.name
                    + f"\nsimilarity: {similarity}`"
                )

                similar[lhs_article_idx] = set(
                    [*similar.get(lhs_article_idx, []), rhs_article_idx]
                )
                similar[rhs_article_idx] = set(
                    [*similar.get(rhs_article_idx, []), lhs_article_idx]
                )

                # Insert into database
                await insert_similar_article_pair_into_db(
                    article1,
                    article2,
                    similarity,
                    client,
                )

    return similar


async def insert_similar_article_pair_into_db(
    article1: NewsArticles, article2: NewsArticles, similarity: float, client: Prisma
):
    await client.similararticles.upsert(
        where={
            "id1_id2": {
                "id1": article1.id,
                "id2": article2.id,
            }
        },
        data={
            "create": {
                "id1": article1.id,
                "id2": article2.id,
                "similarity": similarity,
            },
            "update": {"similarity": similarity},
        },
    )

    await client.similararticles.upsert(
        where={
            "id1_id2": {
                "id1": article2.id,
                "id2": article1.id,
            }
        },
        data={
            "create": {
                "id1": article2.id,
                "id2": article1.id,
                "similarity": similarity,
            },
            "update": {"similarity": similarity},
        },
    )


def calc_tf_idf(
    documents: List[List[str]],
) -> NDArray[np.float32]:
    words: NDArray[np.str_] = np.unique(  # type: ignore
        [word for document in documents for word in document]
    )
    words.sort()

    # Term frequencies per document
    tf_table = np.zeros([len(documents), len(words)])

    for [i, document] in enumerate(documents):
        document_tf_array = calc_norm_term_freq(document, words)
        tf_table[i] = document_tf_array

    # Amount of documents containing the word
    df_counts = np.count_nonzero(tf_table, axis=0)  # type: ignore

    idf_counts = len(words) / df_counts

    # Muliply every row element-wise with the idf_counts col vector
    tf_table *= idf_counts.T

    # Normalize rows
    tf_table /= np.linalg.norm(tf_table, axis=1, keepdims=True)  # type: ignore

    return tf_table


def calc_norm_term_freq(
    document: List[str], words: NDArray[np.str_]
) -> NDArray[np.float32]:
    tf_array = np.zeros(len(words), dtype=float)

    # Count terms occurrences in document
    unique_words, word_count = np.unique(document, return_counts=True)  # type: ignore
    for [i, word] in enumerate(unique_words):
        idx = np.where(words == word)[0][0]  # type: ignore
        tf_array[idx] = word_count[i]

    # Normalize counts
    tf_array /= np.sum(tf_array)  # type: ignore

    return tf_array  # type: ignore


def calc_idf(terms: List[str], documents: List[List[str]]) -> Dict[str, float]:
    idf_table: Dict[str, float] = {}

    # Count term occurrence over documents
    for term in terms:
        for document in documents:
            if term in document:
                idf_table[term] = idf_table.get(term, 0) + 1

    # Normalize counts
    for term in idf_table.keys():
        idf_table[term] = math.log(len(documents) / idf_table[term], 2)

    return idf_table


def extract_tf_idf_values(
    table: Dict[str, Tuple[List[float], float]], article_index: int
) -> Dict[str, float]:
    return {
        term: tf_values[article_index] * idf
        for [term, [tf_values, idf]] in table.items()
    }


def cos_similarity(lhs: Dict[str, float], rhs: Dict[str, float]):
    assert lhs.keys() == rhs.keys()

    # Calculate dot product of both vectors along with the length
    dot_product = 0
    lhs_length_squared = 0
    rhs_length_squared = 0
    for [lhs_tf_idf, rhs_tf_idf] in zip(lhs.values(), rhs.values()):
        dot_product += lhs_tf_idf * rhs_tf_idf
        lhs_length_squared += pow(lhs_tf_idf, 2)
        rhs_length_squared += pow(rhs_tf_idf, 2)

    return dot_product / (math.sqrt(lhs_length_squared * rhs_length_squared))


if __name__ == "__main__":
    asyncio.run(main())

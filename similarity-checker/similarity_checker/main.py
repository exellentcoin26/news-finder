#! /usr/bin/env python3


import asyncio

import sys
import re
import math
import string
from datetime import datetime
import time
from typing import List, Dict, Tuple, Set

from prisma.models import NewsArticles
from prisma import Prisma

import numpy as np
from numpy.typing import NDArray

from utils import filter_stop_words, filter_numerics

THRESHOLD = 0.65


async def main():
    db = Prisma()
    await db.connect()

    # interval in milliseconds
    interval = 4.0e6

    delta = 0.0
    last_time = datetime.now()

    update_override = True

    while True:
        now = datetime.now()
        delta += (now - last_time).total_seconds() * 1e6 / interval
        last_time = now

        if delta >= 1:
            delta -= 1

            retry_count = 0
            while not db.is_connected():
                if retry_count >= 4:
                    raise Exception(
                        "Connecting to database failed 4 times. Aborting application!"
                    )

                try:
                    await db.connect()
                except Exception:
                    retry_count += 1

            should_check = await db.flags.find_unique(
                where={"name": "articles_modified"}
            )

            if should_check is None:
                await db.flags.create({"name": "articles_modified", "value": False})
            elif should_check.value is False and not update_override:
                print(
                    "Nothing modified. Not running similarity checker.", file=sys.stderr
                )
                time.sleep(2)
                continue

            raw_articles = await db.newsarticles.find_many(include={"source": True})

            await calc_article_similarity(raw_articles, db)

            await db.flags.update(
                where={"name": "articles_modified"}, data={"value": False}
            )

            update_override = False


async def calc_article_similarity(
    database_articles: List[NewsArticles], client: Prisma
) -> Dict[int, Set[int]]:
    """
    Calculates the similarity between articles using tf-idf to vectorize text and uses
    cosine similarity.

    Due to performance reasons (for 1000 articles it takes about 15 minutes) it inserts
    the similar markers immediately into the database.
    """

    raw_articles: List[str] = [article.title for article in database_articles]
    raw_descriptions: List[str] = [
        article.description or "" for article in database_articles
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
    cleaned_description: List[str] = [
        re.sub(r"\s+", " ", article)
        .translate(str.maketrans("", "", string.punctuation))
        .lower()
        for article in raw_descriptions
    ]
    # Split articles by whitespace and remove stopwords
    articles = [article.split() for article in cleaned_articles]
    articles = [filter_numerics(article) for article in articles]
    articles = [
        filter_stop_words(article, database_articles[idx].language)
        for [idx, article] in enumerate(articles)
    ]
    descriptions = [description.split() for description in cleaned_description]
    descriptions = [filter_numerics(description) for description in descriptions]
    descriptions = [
        filter_stop_words(description, database_articles[idx].language)
        for [idx, description] in enumerate(descriptions)
    ]

    article_tf_idf_table = calc_tf_idf(articles)
    description_tf_idf_table = calc_tf_idf(descriptions)

    similar: Dict[int, Set[int]] = {}

    title_cosine_similarity_table = np.matmul(
        article_tf_idf_table, article_tf_idf_table.T
    )
    description_cosine_similarity_table = np.matmul(
        description_tf_idf_table, description_tf_idf_table.T
    )

    # Check every article against every other article
    print("Checking cosine similarities...", file=sys.stderr)
    for lhs_article_idx in range(len(articles)):
        for rhs_article_idx in range(lhs_article_idx + 1, len(articles)):
            article1, article2 = (
                database_articles[lhs_article_idx],
                database_articles[rhs_article_idx],
            )
            assert article1.source is not None and article2.source is not None

            title_similarity = title_cosine_similarity_table[lhs_article_idx][
                rhs_article_idx
            ]
            description_similarity = description_cosine_similarity_table[
                lhs_article_idx
            ][rhs_article_idx]

            sys.stdout.write(
                "\r"
                + "\033[2K"
                + f"Article `{lhs_article_idx}` == Article `{rhs_article_idx}`: "
                + f"{title_similarity}".expandtabs(2)
                + f"/{description_similarity}".expandtabs(2)
                + "\r"
            )

            if title_similarity > THRESHOLD:
                sys.stdout.write(
                    "\n"
                    + f"Found:\n\t`{' '.join(articles[lhs_article_idx])}`\n"
                    + "\t"
                    + article1.source.name
                    + "\n\t=="
                    + f"\n\t`{' '.join(articles[rhs_article_idx])}\n"
                    + "\t"
                    + article2.source.name
                    + f"\nsimilarity: {title_similarity}`"
                    + "\n"
                )

                if article1.source.id == article2.source.id:
                    print(
                        f"Found a possible update! ({article1.source.name})",
                        file=sys.stderr,
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
                    title_similarity,
                    client,
                )
            elif (
                title_similarity > np.finfo(float).eps
                and description_similarity > THRESHOLD
                and not (
                    descriptions[lhs_article_idx] == []
                    or descriptions[rhs_article_idx] == []
                )
            ):
                sys.stdout.write(
                    "\n"
                    f"Found:\n\t`{' '.join(articles[lhs_article_idx])}`\n"
                    + "\t"
                    + article1.source.name
                    + "\n\t=="
                    + f"\n\t`{' '.join(articles[rhs_article_idx])}\n"
                    + "\t"
                    + article2.source.name
                    + f"\ndescription similarity: {description_similarity}`"
                    + "\n"
                )

                if article1.source.id == article2.source.id:
                    print(
                        f"Found a possible update! ({article1.source.name})",
                        file=sys.stderr,
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
                    description_similarity,
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

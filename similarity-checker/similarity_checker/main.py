#! /usr/bin/env python3


import asyncio

import sys
import re
import math
import string
from datetime import datetime
from typing import List, Dict, Tuple, Set

import schedule
from prisma import Prisma
from prisma.models import NewsArticles

from utils import Language, filter_stop_words, filter_numerics

THRESHOLD = 0.50

# failsafe for running async call with non async scheduler.
# Note: this fails if the schedule timestep is lower than the starting of the thread
# (which _should_ never happen).
is_running = False

# TODO: check language of the article


async def main():
    schedule.every(30).minutes.do(run)  # pyright: ignore

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

    # Check every article against every other article
    print("Checking cosine similarities...", file=sys.stderr)
    for lhs_article_idx in range(len(articles)):
        for rhs_article_idx in range(lhs_article_idx + 1, len(articles)):
            # Only compare articles from different sources
            article1, article2 = (
                databse_articles[lhs_article_idx],
                databse_articles[rhs_article_idx],
            )
            assert article1.source is not None and article2.source is not None
            if article1.source.id == article2.source.id:
                continue

            similarity = cos_similarity(
                extract_tf_idf_values(tf_idf_table, lhs_article_idx),
                extract_tf_idf_values(tf_idf_table, rhs_article_idx),
            )
            sys.stdout.write(
                "\033[K"
                + f"Article `{lhs_article_idx}` == Article `{rhs_article_idx}`: {similarity}".expandtabs(
                    2
                )
                + "\r"
            )
            if similarity > THRESHOLD:
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
                    client,
                )

    return similar


async def insert_similar_article_pair_into_db(
    article1: NewsArticles, article2: NewsArticles, client: Prisma
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
            },
            "update": {},
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
            },
            "update": {},
        },
    )


def calc_tf_idf(documents: List[List[str]]) -> Dict[str, Tuple[List[float], float]]:
    # Join all frequency values in a single table
    tf_table: Dict[str, List[float]] = {}
    for [doc_idx, document] in enumerate(documents):
        tf = calc_norm_term_freq(document)

        for [term, freq] in tf.items():
            # Insert if term already in table. Create new list with empty entries up
            # until current idx.
            if term not in tf_table:
                # Insert 0 entries
                tf_table[term] = [0 for _ in range(doc_idx)]

            tf_table[term].append(freq)

        # Add 0 entry for terms present in table but not in current document
        for term in tf_table.keys():
            if term not in tf:
                tf_table[term].append(0)

    idf_table = calc_idf(list(tf_table.keys()), documents)
    tf_idf_table = {
        term: (freq, idf_table.get(term, 0)) for [term, freq] in tf_table.items()
    }

    return tf_idf_table


def calc_norm_term_freq(document: List[str]) -> Dict[str, float]:
    tf_table: Dict[str, float] = {}
    total_count = 0

    # Count terms occurrences in document
    for term in document:
        tf_table[term] = tf_table.get(term, 0) + 1
        total_count += 1

    # Normalize counts
    for term in tf_table.keys():
        tf_table[term] /= total_count

    return tf_table


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

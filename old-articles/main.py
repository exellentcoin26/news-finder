import asyncio

import sys
from datetime import datetime

import schedule
from prisma import Prisma


# failsafe for running async call with non async scheduler.
# Note: this fails if the schedule timestep is lower than the starting of the thread
# (which _should_ never happen).
is_running = False


async def main():
    schedule.every(24 * 60).minutes.do(run)  # pyright: ignore

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
    asyncio.get_event_loop().create_task(delete_old_articles())


async def delete_old_articles():
    global is_running

    if is_running:
        print("Not running checker because last run has not finished", file=sys.stderr)
        return

    is_running = True

    db = Prisma()
    await db.connect()
    articles = await db.newsarticles.find_many()
    today = datetime.today()

    for article in articles:
        if article.publication_date is not None:
            delta_article = today - article.publication_date
            if delta_article.days > 2:
                await db.newsarticles.delete(where={"id": article.id})

    await db.disconnect()

    is_running = False


if __name__ == "__main__":
    asyncio.run(main())

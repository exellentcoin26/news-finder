#!/usr/bin/env python3

"""
This script seeds the database with some example RSS feed data.
Note: When the records are already present in the database this script just exits.
"""

import asyncio
from prisma import Prisma
from prisma.errors import UniqueViolationError
from urllib.parse import urlparse, ParseResult


async def main() -> None:
    db = Prisma()
    await db.connect()

    rss_feeds = [
        "https://www.nieuwsblad.be/rss/section/7f1bc231-66e7-49f0-a126-b7346eb3e2fa",
        "https://www.nieuwsblad.be/rss/section/55178e67-15a8-4ddd-a3d8-bfe5708f8932",
        "https://www.nieuwsblad.be/rss/section/5faf0df7-ad4c-4627-8b2e-c764e8b96de1",
        "https://www.nieuwsblad.be/rss/section/b05427b9-b3b0-4da8-8097-5b31209fed52",
        "https://www.standaard.be/rss/section/1f2838d4-99ea-49f0-9102-138784c7ea7c",
        "https://www.standaard.be/rss/section/e70ccf13-a2f0-42b0-8bd3-e32d424a0aa0",
        "https://www.standaard.be/rss/section/8f693cea-dba8-46e4-8575-807d1dc2bcb7",
        "https://www.demorgen.be/in-het-nieuws/rss.xml",
        "https://www.gva.be/rss/section/ca750cdf-3d1e-4621-90ef-a3260118e21c",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://www.vrt.be/vrtnieuws/nl.rss.articles.xml",
        "https://www.vrt.be/vrtnieuws/en.rss.articles.xml",
        "https://sporza.be/nl.rss.xml",
        "https://sporza.be/nl/categorie/auto-motor.rss.xml",
        "https://sporza.be/nl/categorie/zaalsporten/basketbal.rss.xml",
        "https://sporza.be/nl/categorie/voetbal.rss.xml",
        "https://sporza.be/nl/categorie/wielrennen.rss.xml",
        "http://rss.cnn.com/rss/edition_world.rss",
        "http://rss.cnn.com/rss/edition_europe.rss",
        "http://rss.cnn.com/rss/edition_motorsport.rss",
        "https://www.cbsnews.com/latest/rss/science",
        "https://www.cbsnews.com/latest/rss/technology",
        "https://www.cbsnews.com/latest/rss/world",
        "https://www.washingtontimes.com/rss/headlines/news/politics/",
        "https://www.washingtontimes.com/atom/headlines/sports/tennis/",
        "https://telegraph.co.uk/rss.xml",
        "https://moxie.foxnews.com/google-publisher/world.xml",
        "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pIUWlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
    ]

    async with db.batch_() as b:
        for feed in rss_feeds:
            url_components: ParseResult = urlparse(feed)

            news_source = url_components.netloc
            news_source_url = url_components.scheme + "://" + url_components.netloc

            b.newssources.upsert(
                where={"name": news_source},
                data={
                    "create": {
                        "name": news_source,
                        "url": news_source_url,
                        "rss": {"create": {"feed": feed}},
                    },
                    "update": {
                        "rss": {
                            "create": [
                                {
                                    "feed": feed,
                                }
                            ]
                        }
                    },
                },
            )

        try:
            await b.commit()
        except UniqueViolationError:
            pass

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

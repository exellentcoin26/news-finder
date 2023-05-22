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
        ["https://www.nieuwsblad.be/rss/section/7f1bc231-66e7-49f0-a126-b7346eb3e2fa", "Nieuwsblad-buitenland", "Buitenland"],
        ["https://www.nieuwsblad.be/rss/section/55178e67-15a8-4ddd-a3d8-bfe5708f8932", "Nieuwsblad-binnenland", "Binnenland"],
        ["https://www.nieuwsblad.be/rss/section/5faf0df7-ad4c-4627-8b2e-c764e8b96de1", "Nieuwsblad-basketbal", "Basketbal"],
        ["https://www.nieuwsblad.be/rss/section/b05427b9-b3b0-4da8-8097-5b31209fed52", "Nieuwsblad-motorsporten", "Motorsporten"],
        ["https://www.standaard.be/rss/section/1f2838d4-99ea-49f0-9102-138784c7ea7c", "DeStandaard-binnenland", "Binnenland"],
        ["https://www.standaard.be/rss/section/e70ccf13-a2f0-42b0-8bd3-e32d424a0aa0", "DeStandaard-buitenland", "Buitenland"],
        ["https://www.standaard.be/rss/section/8f693cea-dba8-46e4-8575-807d1dc2bcb7", "DeStandaard-sport", "Sport"],
        ["https://www.demorgen.be/politiek/rss.xml", "DeMorgen-politiek", "Politiek"],
        ["https://www.demorgen.be/sport/rss.xml", "DeMorgen-sport", "Sport"],
        ["https://www.gva.be/rss/section/8B7011DF-CAD2-4474-AA90-A2AC00E31B55", "GVA-economie", "Economie"],
        ["https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "NYT-wereldnieuwd", "Wereldnieuws"],
        ["https://www.vrt.be/vrtnieuws/nl.rss.articles.xml", "VRT-wereldnieuws-nl", "Wereldnieuws"],
        ["https://www.vrt.be/vrtnieuws/en.rss.articles.xml", "VRT-wereldnieuws-en", "Wereldnieuws"],
        ["https://sporza.be/nl.rss.xml", "Sporza-sport", "Sport"],
        ["https://sporza.be/nl/categorie/auto-motor.rss.xml", "Sporza-motorsport", "Motorsport"],
        ["https://sporza.be/nl/categorie/zaalsporten/basketbal.rss.xml", "Sporza-basketbal", "Basketbal"],
        ["https://sporza.be/nl/categorie/voetbal.rss.xml", "Sporza-voetbal", "Voetbal"],
        ["https://sporza.be/nl/categorie/wielrennen.rss.xml", "Sporza-wielrennen", "Wielrennen"],
        ["https://www.cbsnews.com/latest/rss/science", "CBS-wetenschap", "Wetenschap"],
        ["https://www.cbsnews.com/latest/rss/technology", "CBS-technology", "Wetenschap"],
        ["https://www.cbsnews.com/latest/rss/world", "CBS-wereldnieuws", "Wereldnieuws"],
        ["https://www.washingtontimes.com/rss/headlines/news/politics/", "WT-politiek", "Politiek"],
        ["https://www.washingtontimes.com/atom/headlines/sports/tennis/", "WT-tennis", "Tennis"],
        ["https://telegraph.co.uk/rss.xml", "Telegraph-wereldnieuws", "Wereldnieuws"],
        ["https://www.nasa.gov/rss/dyn/breaking_news.rss", "Nasa", "Wetenschap"],
    ]

    async with db.batch_() as b:
        for feed in rss_feeds:
            feed_url = feed[0]
            feed_name = feed[1]
            feed_category = feed[2]
            
            url_components: ParseResult = urlparse(feed_url)

            news_source = url_components.netloc
            news_source_url = url_components.scheme + "://" + url_components.netloc

            b.newssources.upsert(
                where={"name": news_source},
                data={
                    "create": {
                        "name": news_source,
                        "url": news_source_url,
                        "rss": {"create": {"feed": feed_url, "name": feed_name, "category": feed_category}},
                    },
                    "update": {
                        "rss": {
                            "create": [
                                {
                                    "feed": feed_url, "name": feed_name, "category": feed_category
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

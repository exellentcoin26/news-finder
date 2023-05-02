#!/usr/bin/env python3

"""
This script clears the entire database.
"""

import asyncio
from prisma import Prisma
from prisma.errors import UniqueViolationError


async def main() -> None:
    db = Prisma()
    await db.connect()

    async with db.batch_() as b:
        b.users.delete_many()
        b.userlogins.delete_many()
        b.usercookies.delete_many()
        b.newssources.delete_many()
        b.rssentries.delete_many()
        b.newsarticles.delete_many()
        b.similararticles.delete_many()
        b.newsarticlelabels.delete_many()

        await b.commit()

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

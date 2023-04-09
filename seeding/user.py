#!/usr/bin/env python3

"""
This script seeds the database with some example user data.
Note: When the records are already present in the database this script just exits.
"""

import asyncio
from prisma import Prisma
from prisma.errors import UniqueViolationError


async def main() -> None:
    db = Prisma()
    await db.connect()

    async with db.batch_() as b:
        b.users.create(
            data={
                "id": 1,
                "username": "laurens",
                "admin": True,
                "login": {"create": {"password": "admin"}},
            }
        )
        b.users.create(
            data={
                "id": 2,
                "username": "jonas",
                "admin": True,
                "login": {"create": {"password": "admin"}},
            }
        )
        b.users.create(
            data={
                "id": 3,
                "username": "david",
                "admin": True,
                "login": {"create": {"password": "admin"}},
            }
        )
        b.users.create(
            data={
                "id": 4,
                "username": "chloë",
                "admin": True,
                "login": {"create": {"password": "admin"}},
            }
        )
        b.users.create(
            data={
                "id": 5,
                "username": "ayoub",
                "admin": True,
                "login": {"create": {"password": "admin"}},
            }
        )

        try:
            await b.commit()
        except UniqueViolationError:
            pass

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

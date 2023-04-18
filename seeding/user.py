#!/usr/bin/env python3

"""
This script seeds the database with some example user data.
Note: When the records are already present in the database this script just exits.
"""

import asyncio
from prisma import Prisma
from prisma.errors import UniqueViolationError
from argon2 import PasswordHasher

users = {
    "laurens": "admin",
    "jonas": "admin",
    "david": "admin",
    "chloë": "admin",
    "ayoub": "admin",
}


async def main() -> None:
    db = Prisma()
    await db.connect()

    async with db.batch_() as b:
        ph = PasswordHasher()
        for [username, password] in users.items():
            hashed_password = ph.hash(password)
            b.users.create(
                data={
                    "username": username,
                    "admin": True,
                    "login": {"create": {"password": hashed_password}},
                },
            )

        try:
            await b.commit()
        except UniqueViolationError:
            pass

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

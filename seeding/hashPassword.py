#!/usr/bin/env python3

"""
This script seeds the database with some hashed password for Users.
Note: When the records are already present in the database this script just exits.
"""
import asyncio
from password_hash.password_hash import *
from prisma import Prisma
from prisma.errors import UniqueViolationError

async def main() -> None:
    db = Prisma()
    await db.connect()

    Users_feed = {
        "Laurens": "deWachter",
        "Jonas" : "Caluwé",
        "David" : "Scalais",
        "Chloe" : "Mansibang",
        "Ayoub" : "ElMarchouchi"
                  }


    async with db.batch_() as b:
        Ph= PasswordHasher()
        for name in Users_feed:
            Ph.setPassword(Users_feed[name])
            Ph.hash()
            hashedPassword = Ph.getHash()
            b.userlogins.upsert(
                data={
                    "create":{
                        "name" : name,
                        "password": hashedPassword,
                }
                  }
        )

        try:
            await b.commit()
        except UniqueViolationError:
            pass
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())


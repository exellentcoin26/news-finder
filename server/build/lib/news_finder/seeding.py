#!/usr/bin/env python3

import asyncio
from prisma import Prisma

# This file seeds an empty database for testing purposes


async def main() -> None:
    db = Prisma()
    await db.connect()

    async with db.batch_() as batcher:
        batcher.users.create(
            data={
                'id': 1,
                'username': 'laurens',
                'admin': True,
                'login': {
                    'create': {
                        'password': 'admin'
                    }
                }
            }
        )
        batcher.users.create(
            data={
                'id': 2,
                'username': 'jonas',
                'admin': True,
                'login': {
                    'create': {
                        'password': 'admin'
                    }
                }
            }
        )
        batcher.users.create(
            data={
                'id': 3,
                'username': 'david',
                'admin': True,
                'login': {
                    'create': {
                        'password': 'admin'
                    }
                }
            }
        )
        batcher.users.create(
            data={
                'id': 4,
                'username': 'chloë',
                'admin': True,
                'login': {
                    'create': {
                        'password': 'admin'
                    }
                }
            }
        )
        batcher.users.create(
            data={
                'id': 5,
                'username': 'ayoub',
                'admin': True,
                'login': {
                    'create': {
                        'password': 'admin'
                    }
                }
            }
        )

    await batcher.commit()
    await db.disconnect()

if __name__ == '__main__':
    asyncio.run(main())

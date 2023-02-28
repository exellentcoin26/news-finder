from prisma import Prisma
from flask import g


async def get_db() -> Prisma:
    """
    Returns the prisma database attached to the flask app context.
    Note: This automatically disconnects and closes the database connection.
    """

    if 'db' not in g:
        db = Prisma()

        await db.connect()
        if not db.is_connected():
            raise Exception("failed to connect to database")

        g.db = db

    assert isinstance(g.db, Prisma), "database instance is a prisma object"
    return g.db

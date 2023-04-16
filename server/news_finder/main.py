#!/usr/bin/env python3

import news_finder.path_setup  # pyright: ignore # noqa
import asyncio
from news_finder.app import get_app


async def main():
    try:
        app = get_app()
        app.run(debug=True, host="0.0.0.0")
    except Exception as e:
        print(e.with_traceback(None))


if __name__ == "__main__":
    asyncio.run(main(), debug=True)

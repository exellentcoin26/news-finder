#!/usr/bin/env python3

import path_setup  # pyright: ignore # noqa
import asyncio
import traceback
import sys
from news_finder.app import get_app


async def main():
    try:
        app = get_app()
        app.run(debug=True, host="0.0.0.0")
    except Exception:
        traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)

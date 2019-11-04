from contextlib import asynccontextmanager
from functools import partial
from urllib.parse import urljoin

import aiohttp


async def fetch_text(session, url):
    async with session.head(url) as response:
        if not "text/html" in response.headers.get("content-type", ""):
            return
    async with session.get(url) as response:
        return await response.text()


async def fetch_text_from_path(session, base, path):
    url = urljoin(base, path)
    # print(url)
    return await fetch_text(session, url)


@asynccontextmanager
async def create_session(domain):
    base = f"https://{domain}"
    session = aiohttp.ClientSession()
    try:
        yield partial(fetch_text_from_path, session, base)
    finally:
        print("closing session")
        await session.close()


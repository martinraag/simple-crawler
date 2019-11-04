from contextlib import asynccontextmanager
from functools import partial
from logging import getLogger
from urllib.parse import urljoin

import aiohttp


log = getLogger(__name__)


async def fetch_text(session, url):
    log.debug(f"Crawl {url=}")
    async with session.head(url) as response:
        if not "text/html" in response.headers.get("content-type", ""):
            log.debug(f"Invalid content type for {url=}")
            return
    async with session.get(url) as response:
        return await response.text()


async def fetch_text_from_path(session, base, path):
    url = urljoin(base, path)
    return await fetch_text(session, url)


@asynccontextmanager
async def create_session(domain):
    base = f"https://{domain}"
    session = aiohttp.ClientSession()
    try:
        yield partial(fetch_text_from_path, session, base)
    finally:
        await session.close()


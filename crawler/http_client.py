from contextlib import asynccontextmanager
from functools import partial
from logging import getLogger
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import aiohttp


USER_AGENT = "MRaagbot/0.1.0 (+https://mraag.xyz)"
log = getLogger(__name__)


async def parse_robots(session, base):
    """Fetches and parses the robots.txt file from a given base URL. Returns an instance of
    RobotFileParser."""

    url = urljoin(base, "robots.txt")
    async with session.get(url) as response:
        text = await response.text()
    robot_parser = RobotFileParser()
    robot_parser.parse(text.splitlines())
    return robot_parser


async def fetch_text(session, url):
    """Fetches the text content of a given url. Yields None if response content type is not
    text/html, otherwise a string of the content."""

    log.debug(f"Crawl {url=}")
    async with session.head(url) as response:
        if not "text/html" in response.headers.get("content-type", ""):
            log.debug(f"Invalid content type for {url=}")
            return
    async with session.get(url) as response:
        return await response.text()


async def fetch_text_from_path(session, base, robots, path):
    """Wraps the fetch function, formats the absolute URL and validates that crawling it is allowed
    by domains robots.txt file."""

    url = urljoin(base, path)
    if not robots.can_fetch(USER_AGENT, url):
        log.warning(f"Skipping url due to Disallow for robots {url=}")
        return
    return await fetch_text(session, url)


@asynccontextmanager
async def create_session(domain):
    """A context manager that creates an HTTP client session and yields a coroutine to fetch the
    text content from a given path."""

    base = f"https://{domain}"
    headers = {"user-agent": USER_AGENT}
    session = aiohttp.ClientSession(headers=headers)
    robots = await parse_robots(session, base)
    try:
        yield partial(fetch_text_from_path, session, base, robots)
    finally:
        await session.close()


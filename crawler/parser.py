import asyncio
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from functools import partial
from urllib.parse import urlparse

from bs4 import BeautifulSoup


def filter_links(links, domain):
    filtered = set()
    for link in links:
        if not link:
            continue
        if link.startswith("/"):
            filtered.add(link)
            continue
        parts = urlparse(link)
        if parts.netloc == domain:
            filtered.add(parts.path if parts.path else "/")
    return filtered


def parse_links(text, domain):
    soup = BeautifulSoup(text, "lxml")
    links = [element.get("href") for element in soup.find_all("a")]
    links = filter_links(links, domain)
    return links


async def run_parser(executor, domain, text):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, parse_links, text, domain)


@contextmanager
def create_parser(domain):
    executor = ProcessPoolExecutor()
    try:
        yield partial(run_parser, executor, domain)
    finally:
        executor.shutdown()

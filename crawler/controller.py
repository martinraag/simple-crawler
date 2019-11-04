import asyncio
from itertools import chain
from functools import partial
from logging import getLogger

from crawler.file_writer import create_file_writer
from crawler.http_client import create_session
from crawler.parser import create_parser


log = getLogger(__name__)


def format_results(path, links):
    return ",".join(chain([path], links))


async def crawl_path(
    path, request_queue, fetch_text, parse_links, write_to_file, visited
):
    text = await fetch_text(path)
    if not text:
        return
    links = await parse_links(text)
    for link in links:
        if link in visited:
            continue
        request_queue.put_nowait(link)
    write_to_file(format_results(path, links))


def on_task_done(tasks, request_queue, done_event, task):
    if task in tasks:
        tasks.remove(task)
    if not tasks and request_queue.empty():
        log.debug(f"Crawl tasks and request queue exhausted")
        done_event.set()
    log.debug(f"Task complete running={len(tasks)} queued={request_queue.qsize()}")


def scheduler(request_queue, fetch_text, parse_links, write_to_file, visited):
    tasks = set()
    done_event = asyncio.Event()
    tasks_done = asyncio.create_task(done_event.wait())

    def schedule_crawl(path):
        task = asyncio.create_task(
            crawl_path(
                path, request_queue, fetch_text, parse_links, write_to_file, visited
            )
        )
        tasks.add(task)
        task.add_done_callback(partial(on_task_done, tasks, request_queue, done_event))
        return task

    return schedule_crawl, tasks_done


async def next_request_or_done(request_queue, tasks_done):
    next_request = asyncio.create_task(request_queue.get())
    done, _ = await asyncio.wait(
        (next_request, tasks_done), return_when=asyncio.FIRST_COMPLETED
    )
    if tasks_done in done:
        next_request.cancel()
        return
    result = done.pop().result()
    return result


async def main(domain, file_path):
    request_queue = asyncio.Queue()
    request_queue.put_nowait("/")
    visited = set()

    with create_parser(domain) as parse_links, create_file_writer(
        file_path
    ) as write_to_file:
        async with create_session(domain) as fetch_text:
            schedule_crawl, tasks_done = scheduler(
                request_queue, fetch_text, parse_links, write_to_file, visited
            )
            while True:
                path = await next_request_or_done(request_queue, tasks_done)
                if not path:
                    log.info(f"Finished crawling {domain=} pages={len(visited)}")
                    break
                if path in visited:
                    log.debug(f"Skipping path already visited {path=}")
                    continue
                log.debug(f"Schedule crawl {path=}")
                visited.add(path)
                schedule_crawl(path)


def crawl(domain, file_path):
    asyncio.run(main(domain, file_path))

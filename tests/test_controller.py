import asyncio
from unittest.mock import Mock

import asynctest
import pytest

from crawler.controller import (
    crawl_path,
    format_results,
    next_request_or_done,
    on_task_done,
)


@pytest.fixture
async def request_queue():
    return asyncio.Queue()


@pytest.fixture
async def done_event():
    return asyncio.Event()


@pytest.fixture
async def tasks_done(done_event):
    return asyncio.create_task(done_event.wait())


@pytest.fixture
async def task():
    async def coro():
        await asyncio.sleep(0.01)

    return asyncio.create_task(coro())


@pytest.fixture
async def fetch_text_mock():
    return asynctest.CoroutineMock(return_value="text")


@pytest.fixture
async def parse_links_mock():
    return asynctest.CoroutineMock(return_value=set(["/", "/foo", "/bar"]))


@pytest.fixture
def write_to_file_mock():
    return Mock()


@pytest.fixture
def request_queue_mock():
    return Mock()


@pytest.mark.asyncio
async def test_next_request_or_done_has_request_not_done(request_queue, tasks_done):
    expected = "/"
    request_queue.put_nowait(expected)
    actual = await next_request_or_done(request_queue, tasks_done)
    assert expected == actual


@pytest.mark.asyncio
async def test_next_request_or_done_no_request_done(
    request_queue, done_event, tasks_done
):
    done_event.set()
    expected = None
    actual = await next_request_or_done(request_queue, tasks_done)
    assert expected == actual


@pytest.mark.asyncio
async def test_next_request_or_done_no_request_done(
    request_queue, done_event, tasks_done
):
    request_queue.put_nowait("/")
    done_event.set()
    expected = None
    actual = await next_request_or_done(request_queue, tasks_done)
    assert expected == actual


@pytest.mark.asyncio
async def test_on_task_done_empty_queue_no_tasks(request_queue, done_event, task):
    tasks = set([task])
    await task
    on_task_done(tasks, request_queue, done_event, task)
    assert not len(tasks)
    assert done_event.is_set()


@pytest.mark.asyncio
async def test_on_task_done_queued_no_tasks(request_queue, done_event, task):
    request_queue.put_nowait("/")
    tasks = set([task])
    await task
    on_task_done(tasks, request_queue, done_event, task)
    assert not len(tasks)
    assert not done_event.is_set()


@pytest.mark.asyncio
async def test_on_task_done_queued_tasks(request_queue, done_event, task):
    tasks = set([task, "foo"])
    await task
    on_task_done(tasks, request_queue, done_event, task)
    assert len(tasks)
    assert not done_event.is_set()


def test_format_results():
    path = "/"
    links = ["/foo", "/bar"]
    expected = "/,/foo,/bar"
    actual = format_results(path, links)
    assert actual == expected


@pytest.mark.asyncio
async def test_crawl_path(
    request_queue_mock, fetch_text_mock, parse_links_mock, write_to_file_mock
):
    path = "/"
    visited = set([path])
    await crawl_path(
        path,
        request_queue_mock,
        fetch_text_mock,
        parse_links_mock,
        write_to_file_mock,
        visited,
    )
    fetch_text_mock.assert_awaited_once_with(path)
    parse_links_mock.assert_awaited_once_with("text")
    write_to_file_mock.assert_called_once()
    request_queue_mock.put_nowait.assert_called()
    assert 2 == request_queue_mock.put_nowait.call_count


@pytest.mark.asyncio
async def test_crawl_path_no_response(
    request_queue_mock, parse_links_mock, write_to_file_mock
):
    path = "/"
    visited = set()
    fetch_text_mock = asynctest.CoroutineMock(return_value=None)
    await crawl_path(
        path,
        request_queue_mock,
        fetch_text_mock,
        parse_links_mock,
        write_to_file_mock,
        visited,
    )
    fetch_text_mock.assert_awaited_once_with(path)
    parse_links_mock.assert_not_awaited()
    write_to_file_mock.assert_not_called()
    request_queue_mock.put_nowait.assert_not_called()

import pytest

from crawler.parser import filter_links


@pytest.fixture
def domain():
    return "marco.org"


def test_filter_links_relative(domain):
    links = ["/", "/foo", "/bar"]
    expected = set(["/", "/foo", "/bar"])
    actual = filter_links(links, domain)
    assert expected == actual


def test_filter_links_absolute(domain):
    links = ["https://marco.org", "https://marco.org/foo", "https://marco.org/bar"]
    expected = set(["/", "/foo", "/bar"])
    actual = filter_links(links, domain)
    assert expected == actual


def test_filter_links_external():
    links = [
        "https://help.marco.org",
        "https://community.marco.org/foo",
        "https://foo.bar/qux",
    ]
    expected = set()
    actual = filter_links(links, domain)
    assert expected == actual

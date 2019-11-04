from argparse import ArgumentTypeError

import pytest

from crawler.cli import valid_domain


def test_valid_domain():
    assert "caseyliss.com" == valid_domain("caseyliss.com")


def test_domain_with_scheme_raises():
    with pytest.raises(ArgumentTypeError):
        valid_domain("https://caseyliss.com")


def test_domain_with_path_raises():
    with pytest.raises(ArgumentTypeError):
        valid_domain("caseyliss.com/*")


def test_invalid_domain_raises():
    with pytest.raises(ArgumentTypeError):
        valid_domain("caseyliss")

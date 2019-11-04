import argparse
import logging
from urllib.parse import urlparse
import sys

from validators import domain

from crawler.controller import crawl


log = logging.getLogger(__name__)


def setup_logging(verbose):
    """Configures the root logger to write to stdout with info level or debug of verbose
    options is set to True."""

    logger = logging.getLogger("crawler")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def valid_domain(value):
    """Ensures a string is a valid domain name or raises ArgumentTypeError."""

    if not domain(value):
        raise argparse.ArgumentTypeError(f"Value {value} is not a valid domain.")
    return value


def cli():
    """Entry point for the command line interface. Parses arguments and starts crawler."""

    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="Domain to crawl.", type=valid_domain)
    parser.add_argument("file_path", help="Path to output file.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    setup_logging(args.verbose)
    log.info(f"Crawl {args.domain=} {args.file_path=}")
    try:
        crawl(args.domain, args.file_path)
    except Exception as err:
        log.exception(err)
        sys.exit(1)


if __name__ == "__main__":
    cli()

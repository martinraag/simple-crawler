import argparse
from urllib.parse import urlparse

from validators import domain

from crawler.controller import crawl


def valid_domain(value):
    if not domain(value):
        raise argparse.ArgumentTypeError(f"Value {value} is not a valid domain.")
    return value


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="Domain to crawl.", type=valid_domain)
    parser.add_argument("file_path", help="Path to output file.")
    args = parser.parse_args()
    crawl(args.domain, args.file_path)


if __name__ == "__main__":
    cli()

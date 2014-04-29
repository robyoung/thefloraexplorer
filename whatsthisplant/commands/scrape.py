"""Scrape plants

Scrape plants various data sources.

Available sources:
    {{sources}}

Usage:
    wtp-scrape [--base-url=<base_url>] SOURCE [SEED ...]
    wtp-scrape (-h | --help)

Options:
    -h --help               Show this help.
    --version               Show version.
    --base-url=<base_url>   Set the base URL
"""
from __future__ import print_function
import sys
import logging
import pkgutil

import docopt

from .. import scrape

logging.basicConfig(level=logging.DEBUG)
for handler in logging.root.handlers:
    handler.addFilter(logging.Filter("whatsthisplant"))


def get_scrapers():
    return [m for _, m, _ in pkgutil.iter_modules(scrape.__path__)]


def run_scraper(scraper, seeds, base_url):
    try:
        module_name = "{}.{}".format(scrape.__name__, scraper)
        module = __import__(module_name, fromlist=[scrape.__name__])
        module.get_plants(seeds, base_url)
    except ImportError:
        print("Unrecognised source '{}'".format(scraper), file=sys.stderr)
        sys.exit(1)


def get_args():
    docstring = __doc__.replace('{{sources}}', "\t\n".join(get_scrapers()))
    return docopt.docopt(docstring, version="0.0.1")


def main():
    args = get_args()
    run_scraper(args['SOURCE'], args['SEED'], args['--base-url'])

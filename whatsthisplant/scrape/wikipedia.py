import requests
import re
import json
from functools import partial

import logging

logger = logging.getLogger(__name__)

import futures

__all__ = ['get_plants']

WIKIPEDIA_URL="http://en.wikipedia.org/w/api.php"
SEED_CATEGORIES=[
    "Category:Trees_by_continent",
    "Category:Trees_by_country",
]

def build_category_query(category, cmtype):
    query = u"format=json&action=query&list=categorymembers&" \
             "cmtitle={}&cmtype={}&cmlimit=500"
    return query.format(category, cmtype)


def build_category_subcategory_query(category):
    return build_category_query(category, "subcat")


def build_category_page_query(category):
    return build_category_query(category, "page")


def build_page_query(title):
    query = u"format=json&action=query&" \
             "titles={}&prop=revisions&rvprop=content"
    return query.format(title)


def query_wikipedia(base_url, query):
    """Run a query against the Wikipedia API"""
    response = requests.get(u"{}?{}".format(base_url, query))
    response.raise_for_status()
    return response.json()


def parse_category_members(data):
    return [member['title'] for member in data['query']['categorymembers']]


def get_categories(base_url, category, categories=None):
    logger.debug("Category: %s", category)
    if categories is None:
        categories = {category}

    data = query_wikipedia(base_url, build_category_subcategory_query(category))
    subcats_to_load = set(parse_category_members(data)) - categories
    categories |= subcats_to_load

    for subcat in subcats_to_load:
        categories |= get_categories(base_url, subcat, categories)

    return categories


def get_all_categories(base_url, categories):
    with futures.ThreadPoolExecutor(len(categories)) as executor:
        return reduce(
            set.union,
            executor.map(
                partial(get_categories, base_url),
                categories))


def get_page_names(base_url, category):
    if isinstance(category, basestring):
        category = [category]

    with futures.ThreadPoolExecutor(50) as executor:
        all_page_names = executor.map(
            partial(get_page_names_for_category, base_url),
            get_all_categories(base_url, category))

        return reduce(set.union, all_page_names)


def get_page_names_for_category(base_url, category):
    logger.debug("Page names: %s", category)
    data = query_wikipedia(base_url, build_category_page_query(category))
    return set(parse_category_members(data))


def get_page_content(base_url, page_name):
    logger.debug("Page: %s", page_name)
    data = query_wikipedia(base_url, build_page_query(page_name))

    return data['query']['pages'].values()[0]['revisions'][0]['*']

# Find scientific classifications:
#  ordo, familia, genus and species (binomial species name)
SCIENTIFIC_CLASSIFICATIONS_PATTERN = re.compile(
    r"\|\s*(ordo|familia|genus|binomial)\s*=\s*['\[]*([^'\]]+)[\]']*")
# Find common names (bolded strings)
COMMON_NAME_PATTERN = re.compile(r"[^']'''([^']+)'''[^']")
def parse_plant_info(content):
    page = {
        "ordo": None,
        "familia": None,
        "genus": None,
        "binomial": None,
        "common_names": [],
    }
    classifications = SCIENTIFIC_CLASSIFICATIONS_PATTERN.findall(content)

    page.update((key, value.lower()) for key, value in classifications)
    
    if page['binomial'] is None:
        return None

    page['common_names'] = [
            n.lower() for n in COMMON_NAME_PATTERN.findall(content)]

    return page


def get_plants(category, base_url):
    if category == [] or category is None:
        category = SEED_CATEGORIES
    if base_url is None:
        base_url = WIKIPEDIA_URL

    page_names = get_page_names(base_url, category)
    with futures.ThreadPoolExecutor(50) as executor:
        page_contents = executor.map(
            partial(get_page_content, base_url),
            page_names)
        pages = map(parse_plant_info, page_contents)

        return filter(None, pages)


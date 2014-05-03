import requests
import re
import json
from functools import partial

import logging

logger = logging.getLogger(__name__)

import futures

__all__ = ['get_plants']

WIKIPEDIA_URL="http://en.wikipedia.org"
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

def build_page_url(base_url, title):
    return u"{}/wiki/{}".format(base_url, title.replace(' ', '_'))


def query_wikipedia(base_url, query):
    """Run a query against the Wikipedia API"""
    response = requests.get(u"{}/w/api.php?{}".format(base_url, query))
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


def get_page(base_url, page_name):
    logger.debug("Page: %s", page_name)
    data = query_wikipedia(base_url, build_page_query(page_name))
    page = data['query']['pages'].values()[0]

    return {
        "name": page_name,
        "url": build_page_url(base_url, page_name),
        "content": page['revisions'][0]['*']
    }

# Find scientific classifications:
#  ordo, familia, genus and species (binomial species name)
SCIENTIFIC_CLASSIFICATIONS_PATTERN = re.compile(
    r"\|\s*(ordo|familia|genus|binomial)\s*=\s*['\[]*([^'\]\n]+)[\]']*")
# Find common names (bolded strings)
COMMON_NAME_PATTERN = re.compile(r"[^']'''([^']+)'''[^']")
def parse_plant_info(page):
    logger.info("Parse plant: %s", page['name'])
    content = page['content']

    plant = {
        "ordo": None,
        "familia": None,
        "genus": None,
        "common_genus": None,
        "binomial": None,
        "common_names": [],
        "links": {
            "wikipedia": page['url']
        }
    }
    classifications = SCIENTIFIC_CLASSIFICATIONS_PATTERN.findall(content)

    plant.update((key, value.lower()) for key, value in classifications)

    if '|' in plant['genus']:
        plant['common_genus'], plant['genus'] = plant['genus'].split('|')

    if plant['binomial'] is None:
        return None

    plant['common_names'] = [
            n.lower() for n in COMMON_NAME_PATTERN.findall(content)]

    return plant


def get_plants(category, base_url):
    if category == [] or category is None:
        category = SEED_CATEGORIES
    if base_url is None:
        base_url = WIKIPEDIA_URL

    page_names = get_page_names(base_url, category)
    logging.info("Got %s page names", len(page_names))
    with futures.ThreadPoolExecutor(50) as executor:
        pages = executor.map(
            partial(get_page, base_url),
            page_names)
        plants = map(parse_plant_info, pages)

        return filter(None, plants)


from nose.tools import eq_

from .wikipedia import parse_plant_info

def test_parse_plant_info_with_common_genus():
    content = """
|genus = spruce|picea
|binomial = picea engelmannii
"""
    page = {"name": "spruce", "url": "", "content": content}
    plant = parse_plant_info(page)

    eq_(plant['genus'], 'picea')
    eq_(plant['common_genus'], 'spruce')


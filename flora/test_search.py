from nose.tools import eq_

from .search import make_index, search, best_match

plants = [
    {"binomial": "fufu bar"},
    {"binomial": "duck hands"},
    {"binomial": "fridge magnet"},
]

def test_make_index():
    index = make_index(plants)

    words = sorted(index.keys())
    eq_(words,
        ['bar', 'duck', 'fridge', 'fufu', 'hands', 'magnet'])


def test_search():
    index = make_index(plants)

    matches = search(index, "fufu bar went to the fridge")

    eq_(len(matches), 2)
    eq_(matches[0].score, 2.0)
    eq_(matches[1].score, 1.0)


def test_best_match():
    index = make_index(plants)

    match = best_match(index, "fufu bar went to the fridge")

    eq_(match.plant['binomial'], "fufu bar")

def test_best_match_only_returns_absolute_matches():
    index = make_index(plants)

    match = best_match(index, "fufu the bar went to the fridge")

    assert match is None

import json
import re
from collections import defaultdict, namedtuple


BaseMatch = namedtuple('BaseMatch', 'plant score')


class Match(BaseMatch):
    def inc_score(self):
        return Match(self.plant, self.score + 1)


def load_index(path):
    with open(path) as f:
        return make_index(json.load(f))


def make_index(plants):
    words = defaultdict(list)
    for plant in plants:
        for word in tokenize(plant['binomial']):
            words[word].append(plant)
    return words


TOKENIZE_RE = re.compile(r'[^\w]+')
def tokenize(string):
    """
    >>> tokenize(u'foo [[bar]] Monkey')
    [u'foo', u'bar', u'monkey']
    """
    return filter(None,
            map(unicode.lower, map(unicode, TOKENIZE_RE.split(string))))


def search(index, string):
    string = string.lower()
    matches = dict()
    for word in tokenize(string):
        for plant in index[word]:
            if plant['binomial'] not in matches:
                matches[plant['binomial']] = Match(plant, 0.0)
            matches[plant['binomial']] = matches[plant['binomial']].inc_score()
    return sorted(
        matches.values(),
        reverse=True,
        key=lambda match: match.score)


def best_match(index, string):
    matches = search(index, string)
    if len(matches) == 0: return None
    
    string = string.lower()
    for match in matches:
        if match.plant['binomial'] in string:
            return match
    return None


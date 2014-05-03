"""A Reddit bot for linking to plant information

Usage:
    flora-reddit [--subreddit=SUBREDDIT] INDEX_PATH

Options:
    --subreddit=SUBREDDIT  The subreddit to run the bot in [default: whatsthisplant].
"""
from datetime import datetime
import logging
import os

import docopt
import praw

from .. import search, utils


logging.basicConfig(
    level=getattr(logging, os.environ.get('LOGLEVEL', 'WARNING')))
for handler in logging.root.handlers:
    handler.addFilter(logging.Filter("flora"))

logger = logging.getLogger(__name__)


def is_bot(comment):
    return "bot" in str(comment.author)


def get_comment_permalink(comment):
    return 'http://www.reddit.com/r/{}/comments/{}?comment={}'.format(
        comment.subreddit.display_name,
        comment.link_id.split('_')[1],
        comment.id)


def run_bot(index_path, subreddit):
    client = praw.Reddit('PRAW The Flora Explorer (thefloraexplorer)')
    client.login()

    index = search.load_index(index_path)

    for comment in client.get_comments(subreddit, limit=200):
        if is_bot(comment):
            logger.info("Skipping bot comment %s", comment.id)
        
        match = search.best_match(index, comment.body)
        if match is not None:
            logger.info("Found match %s '%s' for '%s'",
                    match.plant['binomial'],
                    match.plant['links']['wikipedia'],
                    get_comment_permalink(comment))
            if len(comment.replies) == 0:
                logger.info("No replies to %s, replying", comment.id)
                comment.reply("**{}** on [Wikipedia]({})".format(
                    match.plant['binomial'].capitalize(),
                    match.plant['links']['wikipedia']))
            

def main():
    utils.fix_stdout_encoding()
    args = docopt.docopt(__doc__, version="0.0.1")

    run_bot(args['INDEX_PATH'], args['--subreddit'])

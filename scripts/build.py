import searchtweets
import os
from dotenv import load_dotenv
import re
import requests
import pystache
import pickle
import argparse
import feedparser
from distutils.dir_util import copy_tree
import time
load_dotenv()
DIRNAME = os.path.dirname(__file__)
CACHE_TWEETS_FILE_PATH = os.path.join(DIRNAME, '..', 'tmp', 'tweets.pickle')
CACHE_BLOGPOSTS_FILE_PATH = os.path.join(DIRNAME, '..', 'tmp', 'blogposts.pickle')

def fetch_and_parse_blogposts():
    feed = feedparser.parse("https://blog.dipasquale.fr/feed.xml")
    blogposts = [{
        "title": entry.title,
        "url": entry.link,
        "published_at": time.strftime('%B %-d, %Y', entry.published_parsed)
    } for entry in feed.entries][:2]
    pickle.dump(blogposts, open(CACHE_BLOGPOSTS_FILE_PATH, "wb"))
    return blogposts

def fetch_and_parse_tweets():
    search_args = searchtweets.load_credentials()
    tweets = searchtweets.collect_results(
        {"query": "from:hypertextadrien"},
        max_results=100,
        result_stream_args=search_args
    )
    parsed_tweets = [parse_tweet(status.all_text) for status in tweets]
    parsed_tweets = [t for t in parsed_tweets if t is not None]
    print("%s tweets were fetched." % len(parsed_tweets))
    pickle.dump(parsed_tweets, open(CACHE_TWEETS_FILE_PATH, "wb"))
    return parsed_tweets


def parse_tweet(tweet_text):
    TWEET_REGEX = r"^(?P<title>[^;]*); ?(?P<description>.*) https:\/\/t.co\/(?P<shortened_url_token>\S+) (?P<hashtags>.*)$"
    regex_match = re.match(TWEET_REGEX, tweet_text)
    if not regex_match:
        print("no regex match for '%s'" % tweet_text)
        return None
    parsed = {
        "title": regex_match["title"],
        "description": regex_match["description"],
        "shortened_url_token": regex_match["shortened_url_token"],
        "hashtags": regex_match["hashtags"],
    }
    parsed["hashtags"] = [
        h.strip() for h in parsed["hashtags"].split("#")
    ]
    parsed["hashtags"] = list(
        set(parsed["hashtags"]) - set(["hypertext", ""])
    )
    parsed["hashtags"] = [{"name": h} for h in parsed["hashtags"]]
    parsed["url"] = requests.get(
        "https://t.co/%s" % parsed["shortened_url_token"],
        allow_redirects=False
    ).headers['Location']
    return parsed


def rebuild(tweets, blogposts):
    template_path = os.path.join(DIRNAME, '..', 'index.mustache')
    renderer = pystache.Renderer()
    rendered_html = renderer.render_path(
        template_path, {
            "tweets": tweets,
            "blogposts": blogposts
        }
    )
    index_path = os.path.join(DIRNAME, '..', 'build', 'index.html')
    file = open(index_path, 'w')
    file.write(rendered_html)
    file.close()
    copy_tree(
        os.path.join(DIRNAME, "..", "static_assets"),
        os.path.join(DIRNAME, "..", "build")
    )
    print("rebuild done.")


def create_tmp_directories():
    for dir_name in ["tmp", "build"]:
        path = os.path.join(DIRNAME, '..', dir_name)
        if not os.path.exists(path):
            os.makedirs(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--use-cache', const=True, action='store_const')
    args = parser.parse_args()
    create_tmp_directories()
    if args.use_cache and os.path.isfile(CACHE_TWEETS_FILE_PATH):
        tweets = pickle.load(open(CACHE_TWEETS_FILE_PATH, "rb"))
        blogposts = pickle.load(open(CACHE_BLOGPOSTS_FILE_PATH, "rb"))
        print("%s tweets and %s blogposts loaded from cache" % (len(tweets), len(blogposts)))
    else:
        tweets = fetch_and_parse_tweets()
        blogposts = fetch_and_parse_blogposts()
    rebuild(tweets, blogposts)
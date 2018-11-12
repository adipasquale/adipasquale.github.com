import twitter
import os
from dotenv import load_dotenv
import re
import requests
import pystache
import pickle
import argparse
from distutils.dir_util import copy_tree
load_dotenv()
DIRNAME = os.path.dirname(__file__)
CACHE_FILE_PATH = os.path.join(DIRNAME, '..', 'tmp', 'tweets.pickle')


def fetch_and_parse_tweets():
    api = twitter.Api(
        consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
        consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
        access_token_key=os.environ["TWITTER_ACCESS_TOKEN_KEY"],
        access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
    )

    results = api.GetSearch(
        raw_query="q=%23hypertext from%3AMagalitoRene&tweet_mode=extended"
    )
    parsed_tweets = [parse_tweet(status.full_text) for status in results]
    print("%s tweets were fetched." % len(parsed_tweets))
    pickle.dump(parsed_tweets, open(CACHE_FILE_PATH, "wb"))
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


def rebuild(tweets):
    template_path = os.path.join(DIRNAME, '..', 'index.mustache')
    renderer = pystache.Renderer()
    rendered_html = renderer.render_path(
        template_path, {
        "tweets": tweets
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
    if args.use_cache and os.path.isfile(CACHE_FILE_PATH):
        tweets = pickle.load(open(CACHE_FILE_PATH, "rb"))
        print("%s tweets loaded from cache" % len(tweets))
        print([t["hashtags"] for t in tweets])
    else:
        tweets = fetch_and_parse_tweets()
    rebuild(tweets)
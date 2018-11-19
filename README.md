# adipasquale.github.com

The code for my personal website accessible here : https://www.dipasquale.fr

## How does it work ?

This is a very simple Python application that builds a static `index.html` file. It's only job is to fetch my tweets and render the HTML template. It uses the [Mustache](https://mustache.github.io/) templating language, and only the [Tachyons CSS Framework](http://tachyons.io/) for styling.


## Local setup

```
mkvirtualenv adipasquale.github.com
pip3 install -r requirements.txt -r requirements-dev.txt
```

You will also need to create a Twitter App, and enter it's credentials into a local `.env` file :

```
TWITTER_CONSUMER_KEY=...
TWITTER_CONSUMER_SECRET=...
TWITTER_ACCESS_TOKEN_KEY=...
TWITTER_ACCESS_TOKEN_SECRET=...
```

## Local serve

```
workon adipasquale.github.com
python3 scripts/local_server.py
```

This will rebuild `build/index.html` and auto-reload when necessary :

- when the `index.mustache` is updated, it uses a tweets cache
- when the `build.py` file is updated, it re-fetches the tweets

# -*- coding: utf-8 -*-

import re
import random

import bs4
import requests
import furl
import time


HOME = furl.furl("http://www.brainyquote.com")

# def tosuffix(s):
#     return ''.join(c.lower() for c in s if c.isalpha())
TOPICS = ['Motivational', 'Friendship', 'Love', 'Smile', 'Life', 'Inspirational', 'Family', 'Nature', 'Positive', 'Attitude']

def fix(name):
    """Fix a name

    e. e. cummings => E. E. Cummings

    Arguments:
        name {str} -- the name of an author
    """
    return ' '.join(n.capitalize() for n in name.split(' '))


def get_page_with_retries(url, sleep=3, max_tries=10):
    response = None
    cur_try = 0
    while (not(response) and (cur_try <= max_tries)):
        cur_try = cur_try + 1
        response = requests.get(url)
        if "Too many requests" in response.text:
            time.sleep(sleep)
            response = None
    return response


def get_quotes(url, filter=None):
    response = get_page_with_retries(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    quotes = soup.find('div', {'id':'quotesList'})
    quotes = []
    for q in quotes.children:
        if isinstance(q, bs4.element.Tag):
            text = q.find('a', {'title': 'view quote'})
            author = q.find('a', {'title': 'view author'})
            if text and author:
                quote = Quote(text=text.text, author=fix(author.text))
                quotes.append(quote)
    return quotes


def get_topics():
    # get all topics
    url = HOME / 'topics'
    response = get_page_with_retries(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    topics = soup.find_all('div', {'class':'row bq_left'})[1]
    return [t.text for t in topics.find_all('span', {'class':'topicContentName'})]


def get_popular_topics():
    # get a list of popular topics
    url = HOME / 'topics'
    response = get_page_with_retries(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    topics = soup.find_all('div', {'class':'row bq_left'})[1]
    return [t.text for t in topics.find_all('span', {'class':'topicContentName'}) if t.next_sibling.next_sibling.name == 'img']


def get_authors():
    # get the list of authors
    url = HOME / 'authors'
    response = get_page_with_retries(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    return [t.text.strip() for t in soup.find_all('span', {'class':'authorContentName'})]


# class BaseSearcher filter

class Quote(object):
    """Quote class

    Quotes of famous peaple

    Example
    -------
    >>> q = Quote.today()
    >>> print(q)   # 2018-10-25
    >>> He that lives upon hope will die fasting. --- Benjamin Franklin

    >>> quote = Quote.random(topic='love')
    >>> print(quote)
    >>> The greatest healing therapy is friendship and love. --- Hubert H. Humphrey
    """

    __slots__ = ('content', 'topic', 'author', 'info')

    def __init__(self, content='', topic='', author='', info=''):
        """
        Keyword Arguments:
            content {str} -- [content of the quote] (default: {''})
            topic {str} -- [topic of the quote] (default: {''})
            author {str} -- [the author] (default: {''})
            info {str} -- related information (default: {''})
        """
        self.content = content
        self.topic = topic
        self.author = author
        self.info = info

    def __str__(self):
        return '{0:tight}'.format(self)

    def __repr__(self):
        return 'Quote ({0.topic}): {0}'.format(self)

    def __format__(self, spec):
        if spec == 'signature':
            return ('--- ' + self.author).rjust(len(self.content))
        elif spec == 'content':
            return self.content
        elif spec == 'tight':
            return '{0.content} --- {0.author}'.format(self)
        elif spec.isdigit():
            c = int(spec)
            words = '{0:tight}'.format(self).split(' ')
            L = len(words)
            n, r = divmod(L, c)
            return '\n'.join([' '.join(words[i:i+c]) for i in range(n)] + [' '.join(words[n*c:n*c+r])])
        else:
            L = len(self.content)
            return '{0:content}\n{0:signature}'.format(self)

    def pretty(self):
        return '{0:7}'.format(self)

    def toHTML(self):
        # translate to HTML, applied in uberschit widgets
        return """
  <div class="quote">
    <div class="content">{0.content}</div>
    <div class="author">--- {0.author}</div>
  </div>""".format(self)

    def toXML(self):
        return """
  <quote>
    <content>{0.content}</content>
    <author>--- {0.author}</author>
  </quote>""".format(self)

    def __getstate__(self):
        return {prop: getattr(self, prop) for prop in Quote.__slots__}

    def __setstate__(self, state):
        for prop in Quote.__slots__:
            setattr(self, prop, state.get(prop, ""))

    @staticmethod
    def random(*args, **kwargs):
        return random.choice(Quote.find_all(*args, **kwargs))

    @staticmethod
    def find(*args, **kwargs):
        return Quote.find_all(*args, **kwargs)[0]

    @staticmethod
    def find_all(topic='', author='', index='', delay_between_calls = 2):
        if topic:
            if (isinstance(topic, list)):
                quotes = []
                for cur_topic in topic:
                    cur_quotes = Quote.find_all(topic=cur_topic)
                    quotes.extend(cur_quotes)
                    time.sleep(delay_between_calls)
            else:
                url = HOME / ('topics/%s' % topic)
                response = get_page_with_retries(url)
                soup = bs4.BeautifulSoup(response.text, "lxml")
                tags = soup.find('div', {'id':'quotesList'})
                quotes = [Quote.fromTag(tag) for tag in tags.find_all('div', {'class':'clearfix'})]
                if author:
                    quotes = [quote for quote in quotes if quote.author == author]
        else:
            if author:
                url = HOME / ('authors/%s' % author)
                response = get_page_with_retries(url)
                soup = bs4.BeautifulSoup(response.text, "lxml")
                tags = soup.find('div', {'id':'quotesList'})
                quotes = [Quote.fromTag(tag) for tag in tags.find_all('div', {'class':'clearfix'})]
            else:
                quotes = []
                for topic in TOPICS:
                    quotes = Quote.find_all(topic=topic)
                    quotes.extend(quotes)
                    time.sleep(delay_between_calls)
        return quotes

    @staticmethod
    def fromTag(tag):
        content = tag.find('a', {'title': 'view quote'})
        author = tag.find('a', {'title': 'view author'})
        return Quote(content=content.text, author=fix(author.text))

    @staticmethod
    def today(topic=None):
        # get today quote
        url = HOME / 'quote_of_the_day'
        response = get_page_with_retries(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        container = soup.find('div', {'class': 'container bqQOTD'})

        if isinstance(topic, str):
            quote_of_the_day = [topic.capitalize()]
        elif isinstance(topic, (tuple, list, set)):
            quote_of_the_day = [t.capitalize() for t in topic]
        else:
            quote_of_the_day = ['']
        def f(tag):
            try:
                t = tag.find('h2', {'class':'qotd-h2'}).text.partition('Quote of the Day')[0]
                return t in quote_of_the_day
            except:
                pass
        try:
            return Quote.fromTag(container.find(f).find('div', {'class': 'clearfix'}))
        except:
            return defaultQuote

    @staticmethod
    def read_yaml(fname, topic=None):
        import yaml
        with open(fname) as fo:
            quotes = yaml.full_load(fo)
        return map(lambda d: Quote(**d) if isinstance(d, dict) else d, quotes)

    @staticmethod
    def choice_yaml(fname, topic=None):
        import yaml
        with open(fname) as fo:
            d = random.choice(yaml.full_load(fo))
        return Quote(**d) if isinstance(d, dict) else d


defaultQuote = Quote(content='Je pense, donc je suis.', topic='Reason', author='Rene Descartes')

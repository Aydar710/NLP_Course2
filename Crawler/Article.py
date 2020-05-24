import json


class Article:

    def __init__(self, name="", authors=None, year="", journal="", annotation="", key_words=None, category=""):
        if key_words is None:
            key_words = []
        if authors is None:
            authors = []
        self.name = name
        self.authors = authors
        self.year = year
        self.journal = journal
        self.annotation = annotation
        self.key_words = key_words
        self.category = category

    def __str__(self):
        return 'name: ' + self.name + "\n" \
               + 'authors: ' + self.authors.__str__() + "\n" \
               + 'year: ' + self.year + "\n" \
               + 'journal: ' + self.journal + "\n" \
               + 'annotation: ' + self.annotation + "\n" \
               + 'key_words: ' + self.key_words.__str__() + "\n" \
               + 'category: ' + self.category


class ArticleEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Article):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)
import pandas
import nltk
import random
import pickle
import gensim

from spacy.lang.ru import Russian
from spacy_russian_tokenizer import RussianTokenizer, MERGE_PATTERNS
from nltk.corpus import wordnet as wn
from gensim import corpora
from pprint import pprint

parser = Russian()
russian_tokenizer = RussianTokenizer(parser, MERGE_PATTERNS)
parser.add_pipe(russian_tokenizer, name='russian_tokenizer')


def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    print([token.text for token in tokens])
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens


nltk.download('wordnet')


def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


nltk.download('stopwords')
ru_stop = set(nltk.corpus.stopwords.words('russian'))


def prepare_text_for_lda(text):
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in ru_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens


text_data = []
df = pandas.read_csv("reviews.csv", encoding="utf-8")
reviews = df['text']

for review in reviews:
    print(review)
    tokens = prepare_text_for_lda(review)
    if random.random() > .99:
        print(tokens)
        text_data.append(tokens)

dictionary = corpora.Dictionary(text_data)
corpus = [dictionary.doc2bow(text) for text in text_data]

pickle.dump(corpus, open('corpus.pkl', 'wb'))
dictionary.save('dictionary.gensim')

NUM_TOPICS = 10
NUM_WORDS = 15

model_name = "model.gensim"
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=NUM_TOPICS, id2word=dictionary, passes=15)
ldamodel.save(model_name)
topics = ldamodel.print_topics(num_words=NUM_WORDS)
for topic in topics:
    print(topic)

top_topics = ldamodel.top_topics(corpus)

avg_topic_coherence = sum([t[1] for t in top_topics]) / NUM_TOPICS
print('Average topic coherence: %.4f.' % avg_topic_coherence)

pprint(top_topics)

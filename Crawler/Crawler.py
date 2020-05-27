import requests
from bs4 import BeautifulSoup
import json

from Article import Article, ArticleEncoder

BASE_ARTICLE_URL = "https://cyberleninka.ru/article/c"
BASE_URL = "https://cyberleninka.ru/"
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'accept': '*/*'}

ARTICLE_CATEGORIES = ['basic-medicine', 'clinical-medicine', 'health-sciences', 'health-biotechnology']


def get_article_pages_html(category, page=1):
    url = BASE_ARTICLE_URL + '/' + category + '/' + str(page)
    r = requests.get(url=url, headers=HEADERS)
    return r


def get_article_html(link):
    r = requests.get(url=link, headers=HEADERS)
    return r


def parse_article(article_link):
    html = get_article_html(article_link)
    if html.status_code == 200:
        return get_article_content(html.text)
    else:
        print("Ошибка при получении страницы. Код ответа" + html.status_code)


def get_article_content(html):
    doc = BeautifulSoup(html, 'html.parser')
    article = Article()

    # annotation
    try:
        abstract_p = doc.find('div', class_='full abstract').find_next('p')
        article.annotation = abstract_p.text
    except AttributeError:
        print("Нет аннотации")
        return

    # name, category
    content_div = doc.find('div', class_='cover mobhide').find_next('div')
    article.name = content_div.find('i').text
    article.category = content_div.find('span').find('i').text

    # authors
    for meta in doc.find_all('meta'):
        if meta.get('name') == 'citation_author':
            article.authors.append(meta.get('content'))

    # journal
    journal_year_div = content_div.find_all('div', class_='half')
    journal = journal_year_div[1].find('span').get_text()
    article.journal = journal

    # year
    year = journal_year_div[1].find('div', class_='label year').text
    article.year = year

    # key_words
    try:
        key_words_spans = doc.find('div', class_='full keywords').find_all('span', class_='hl to-search')
        for key_word in key_words_spans:
            article.key_words.append(key_word.text)
    except AttributeError:
        print("Нет ключевых слов")

    return article


def get_articles_should_for_parsing(html):
    article_links = []
    doc = BeautifulSoup(html, 'html.parser')
    list = doc.find('ul', class_='list').find_all('li')
    for item in list:
        article_link = BASE_URL + item.find_next('a').get('href')
        annotation = item.find_next('p').text
        if len(annotation) > 0:
            article_links.append(article_link)

    return article_links, len(list) == 0


for category in ARTICLE_CATEGORIES:
    page = 1
    has_pages = True
    while has_pages:
        print('Parsing ' + ' page ' + str(page))
        html = get_article_pages_html(category, page).text
        article_links, is_last_page = get_articles_should_for_parsing(html)
        if not is_last_page:
            for link in article_links:
                article = parse_article(link)
                print("Parsed: " + article.name)

                article_json = json.dumps(article, cls=ArticleEncoder, ensure_ascii=False)
                f = open('articles.txt', 'a', encoding='utf-8')
                f.write(article_json + "\n")
                f.close()

            page += 1
        else:
            has_pages = False

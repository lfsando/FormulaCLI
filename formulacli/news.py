import re
from typing import Dict, Pattern, Union, List

from bs4 import BeautifulSoup
from pandas import DataFrame

from formulacli.html_handlers import get_response, parse
from formulacli.urls import BASE_URL, LATEST_NEWS_URL


def parse_top_stories(soup: BeautifulSoup, img_size: int = 1) -> List[Dict[str, Union[str, List[str]]]]:
    article_html = soup.find_all("div", {"class": "col-lg-6 col-md-12"})

    img_group_pat: Pattern[str] = re.compile(r'(^.*transform/)(\d)(col/\w+\.\w+$)')
    img_size_sub: str = r'\g<1>' + str(img_size) + r'\g<3>'

    articles: List[Dict[str, Union[str, List[str]]]] = []

    main_div: BeautifulSoup = article_html[0]
    main_img_url: str = main_div.find(name='picture').img['src']
    main_captions: BeautifulSoup = main_div.find(name="div", attrs={'class': 'f1-cc--caption'}).select('p')
    main_story: Dict[str, Union[str, List[str]]] = {
        'headline': main_captions[1].text,
        'tags': ['main-story', main_captions[0].text.strip().lower()],
        'url': BASE_URL + main_div.a['href'],
        'img': img_group_pat.sub(img_size_sub, main_img_url)
    }
    articles.append(main_story)

    top_stories_html: BeautifulSoup = article_html[1].div
    for story in top_stories_html.find_all('a'):
        text: str = story.text.strip().split('\n')
        img_tag: Union[Dict, BeautifulSoup] = {}
        try:
            img_tag = story.find('picture').img
        except AttributeError:
            # no picture in article
            pass
        img_url: str = img_tag.get('src', '')
        st: Dict[str, Union[str, List[str]]] = {
            'headline': text[-1],
            'tags': [text[0]],
            'url': BASE_URL + story['href'],
            'img': img_group_pat.sub(img_size_sub, img_url)
        }
        articles.append(st)
    return articles


def fetch_top_stories(img_size: int = 1) -> DataFrame:
    resp: str = get_response(LATEST_NEWS_URL)
    soup: BeautifulSoup = parse(resp)
    top_stories: List[Dict[str, Union[str, List[str]]]] = parse_top_stories(soup, img_size=img_size)
    return DataFrame(top_stories)

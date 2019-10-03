import pytest
import requests
from bs4 import BeautifulSoup

from urllib3 import HTTPResponse

from formulacli import html_handlers
from formulacli.html_handlers import parse


def test_get_response():
    response = html_handlers.get_response('http://216.58.192.142')
    assert isinstance(response, str)
    response = html_handlers.get_response('https://www.python.org/static/community_logos/python-logo.png', b=True)
    assert isinstance(response, HTTPResponse)


def test_parse():
    response = requests.get('http://216.58.192.142')
    soup = parse(response.text)
    assert isinstance(soup, BeautifulSoup)
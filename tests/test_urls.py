import pytest
import requests

from formulacli import urls


def test_base_url_connection():
    resp = requests.get(urls.BASE_URL)
    assert resp.status_code == 200


def test_drivers_url_connection():
    resp = requests.get(urls.DRIVERS_URL)
    assert resp.status_code == 200


def test_latest_news_connection():
    resp = requests.get(urls.LATEST_NEWS_URL)
    assert resp.status_code == 200

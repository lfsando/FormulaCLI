from typing import Dict, Any, Tuple, Iterator, List

from bs4 import BeautifulSoup
from pandas import DataFrame

from .urls import BASE_URL, DRIVERS_URL
from .html_handlers import get_response, parse


def parse_drivers(soup: BeautifulSoup) -> DataFrame:
    drivers_div = soup.select(".driver-index-teasers a")
    drivers: List[Dict[str, str]] = []

    for driver_div in drivers_div:
        driver: Dict[str, str] = {
            "NAME": driver_div.find("h1", class_='driver-name').text.strip(),
            "NUMBER": driver_div.find("div", class_='driver-number').text.strip(),
            "TEAM": driver_div.find("p", class_='driver-team').text.strip(),
            "URL": BASE_URL + driver_div['href'],
            "IMG": BASE_URL + driver_div.figure.img["src"]
        }

        drivers.append(driver)
    return DataFrame(drivers)


def parse_driver(soup: BeautifulSoup) -> Dict[str, str]:
    info_table = soup.find('table', class_='stat-list').tbody
    zipped_info: Iterator[Tuple[Any, Any]] = zip(info_table.find_all("th"), info_table.find_all("td"))
    driver_info = [(k.text.strip().upper(), v.text.strip()) for k, v in zipped_info]
    driver: Dict[str, str] = {}
    for k, v in driver_info:
        driver[k] = v

    bio_div = soup.find('section', class_='biography')
    bio: str = ""
    for p in bio_div.find_all('div', 'text')[1].find_all("p"):
        bio += p.text.strip() + '\n'
    driver["BIO"] = bio
    return driver


def fetch_drivers() -> DataFrame:
    url: str = DRIVERS_URL

    response: str = get_response(url)
    soup: BeautifulSoup = parse(response)

    drivers: DataFrame = parse_drivers(soup)
    return drivers


def fetch_driver(url: str) -> Dict[str, str]:
    response: str = get_response(url)
    soup: BeautifulSoup = parse(response)
    driver: Dict[str, str] = parse_driver(soup)
    return driver

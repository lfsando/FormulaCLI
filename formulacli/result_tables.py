from datetime import datetime
from typing import Optional, List

from pandas import DataFrame
from bs4 import BeautifulSoup

from formulacli.html_handlers import get_response, parse


def get_result_table(soup: BeautifulSoup) -> Optional[BeautifulSoup]:
    try:
        table: BeautifulSoup = soup.select("table.resultsarchive-table")[0]
        return table
    except IndexError:
        return None


def get_cols(table: BeautifulSoup) -> List[str]:
    cols: List[str] = []
    for th in table.thead.find_all("th"):
        col: Optional[str] = th.text
        if col:
            cols.append(col.upper())
    return cols


def get_values(table: BeautifulSoup) -> List[List[str]]:
    entries: List[List[str]] = []
    for tr in table.tbody.find_all("tr"):
        entry = []
        for td in tr.find_all("td"):
            if td.text:
                entry.append(td.text.strip().replace("\n", " "))
        entries.append(entry)
    return entries


def fetch_results(_for: str = "drivers", year: Optional[int] = None) -> DataFrame:
    if not year:
        year = datetime.now().year

    url: str = f"https://www.formula1.com/en/results.html/{year}/{_for}.html"

    table: Optional[BeautifulSoup] = get_result_table(parse(get_response(url)))
    if table is None:
        raise ValueError("Invalid Season Year")
    cols: List[str] = get_cols(table)
    entries: List[List[str]] = get_values(table)

    return DataFrame(entries, columns=cols)

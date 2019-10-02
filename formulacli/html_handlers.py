from typing import Union

import requests
from bs4 import BeautifulSoup
from requests import Response
from urllib3 import HTTPResponse


def get_response(url: str, b: bool = False) -> Union[str, HTTPResponse]:
    if b:
        response: Response = requests.get(url, stream=True)
        return response.raw
    else:
        response = requests.get(url)
        response.encoding = "utf-8"
        return response.text
            

def parse(response: str) -> BeautifulSoup:
    return BeautifulSoup(response, 'html.parser')

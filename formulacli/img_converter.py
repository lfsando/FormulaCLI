from typing import Tuple, Dict, Optional, Union

from math import sqrt
from numpy import array
from PIL import Image
from colorama import init, Back, Style, Fore
from urllib3 import HTTPResponse

from formulacli.html_handlers import get_response

init(convert=True)

BACK_BW_SCHEME: Dict[Tuple[int, int, int], str] = {
    (0, 0, 0): Back.BLACK,
    (61, 61, 61): Back.LIGHTBLACK_EX,
    (210, 180, 140): Back.LIGHTWHITE_EX,
    (255, 255, 0): Back.WHITE
}

BACK_COLOR_SCHEME: Dict[Tuple[int, int, int], str] = {
    (0, 0, 255): Back.BLUE,
    (0, 255, 255): Back.CYAN,
    (0, 128, 0): Back.GREEN,
    (65, 105, 225): Back.LIGHTBLUE_EX,
    (46, 139, 87): Back.LIGHTCYAN_EX,
    (186, 85, 211): Back.LIGHTGREEN_EX,
    (220, 20, 60): Back.LIGHTMAGENTA_EX,
    (189, 189, 189): Back.LIGHTRED_EX,
    (218, 112, 214): Back.LIGHTYELLOW_EX,
    (255, 0, 0): Back.MAGENTA,
    (255, 255, 255): Back.RED,
}
FRONT_BW_SCHEME: Dict[Tuple[int, int, int], str] = {
    (0, 0, 0): Fore.BLACK,
    (61, 61, 61): Fore.LIGHTBLACK_EX,
    (210, 180, 140): Fore.LIGHTWHITE_EX,
    (255, 255, 0): Fore.WHITE
}

FRONT_COLOR_SCHEME: Dict[Tuple[int, int, int], str] = {
    (0, 0, 255): Fore.BLUE,
    (0, 255, 255): Fore.CYAN,
    (0, 128, 0): Fore.GREEN,
    (65, 105, 225): Fore.LIGHTBLUE_EX,
    (46, 139, 87): Fore.LIGHTCYAN_EX,
    (186, 85, 211): Fore.LIGHTGREEN_EX,
    (220, 20, 60): Fore.LIGHTMAGENTA_EX,
    (189, 189, 189): Fore.LIGHTRED_EX,
    (218, 112, 214): Fore.LIGHTYELLOW_EX,
    (255, 0, 0): Fore.MAGENTA,
    (255, 255, 255): Fore.RED,
}


def distance(c1, c2) -> float:
    (r1, g1, b1) = c1
    (r2, g2, b2) = c2
    return sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def color_to_ansi(px: Tuple[int, int, int], colors: Dict[Tuple[int, int, int], str]) -> str:
    if colors is None:
        raise ValueError
    min_val: float = 256.0
    min_col: str = ""
    for i, (rgb, color) in enumerate(colors.items()):
        dist: float = distance(rgb, px)
        if dist < min_val:
            min_val = dist
            min_col = color
        if dist < 10:
            break
    return min_col + Style.BRIGHT


def convert_image(
        url: str,
        brush: Optional[str] = None,
        colored: bool = False,
        ratio: Tuple[Union[float, int], Union[float, int]] = (1, 1),
        size: Optional[Tuple[int, int]] = None,
        crop_box: Optional[Tuple[int, int, int, int]] = None) -> str:
    im_bytes: HTTPResponse = get_response(url, b=True)
    image: Image = Image.open(im_bytes)
    if crop_box is not None:
        image = image.crop(crop_box)

    if ratio and size:
        image = image.resize((
            round(size[0] * ratio[0]),
            round(size[1] * ratio[1])
        ))
    elif size:
        image = image.resize(size)
    elif ratio:
        image = image.resize((round(image.size[0] * ratio[0]), round(image.size[1] * ratio[1])))

    return paint_image(image, colored=colored, brush=brush)


def paint_image(im: Image,
                color_scheme: Optional[Dict[Tuple[int, int, int], str]] = None,
                colored: bool = False,
                brush: Optional[str] = None,
                ) -> str:
    if brush is None:
        brush = " "
        if colored:
            color_scheme = BACK_COLOR_SCHEME
        else:
            color_scheme = BACK_BW_SCHEME
    else:
        if colored:
            color_scheme = FRONT_COLOR_SCHEME
        else:
            color_scheme = FRONT_BW_SCHEME

    initial_pixels: array = array(im)
    picture: str = ""
    for i, row in enumerate(initial_pixels):
        for j, px in enumerate(row):
            picture += color_to_ansi(px, color_scheme)
            picture += brush
        picture += "\n"
    picture += Back.RESET
    picture += Fore.RESET
    picture += Style.RESET_ALL
    return picture

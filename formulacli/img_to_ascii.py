from typing import Tuple, Dict, Optional

import math
import numpy as np
from PIL import Image
from colorama import init, Back, Style

init(convert=True)

COLOR_SCHEME: Dict[Tuple[int, int, int], str] = {
    (0, 0, 0): Back.BLACK,
    (61, 61, 61): Back.LIGHTBLACK_EX,
    (210, 180, 140): Back.LIGHTWHITE_EX,
    (255, 255, 0): Back.WHITE
}

COLORED_SCHEME: Dict[Tuple[int, int, int], str] = {
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


def distance(c1, c2) -> float:
    (r1, g1, b1) = c1
    (r2, g2, b2) = c2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def color_to_ansi(px: Tuple[int, int, int], colors: Dict[Tuple[int, int, int], str]) -> str:
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


def convert(im: Image,
            size: Tuple[int, int] = (55, 25),
            colored: bool = False,
            color_scheme: Optional[Dict[Tuple[int, int, int], str]] = None,
            cropped: Tuple[int, int, int, int] = (100, 10, 220, 130)) -> str:
    if not color_scheme:
        color_scheme = COLOR_SCHEME
    if cropped:
        im = im.crop(cropped)
    if size:
        im = im.resize(size)

    initial_pixels: np.array = np.array(im)
    photo: str = ""
    for i, row in enumerate(initial_pixels):
        for j, px in enumerate(row):
            if colored and color_scheme:
                photo += color_to_ansi(px, color_scheme)
            photo += " "
        photo += "\n"
    photo += Back.RESET
    photo += Style.RESET_ALL
    return photo

import random
from typing import List, Optional

from colorama import Fore, Back, Style

banners = ["""
        ______                           __         ___     
       / ____/___  _________ ___  __  __/ /___ _   <  /     
      / /_  / __ \/ ___/ __ `__ \/ / / / / __ `/   / /      
     / __/ / /_/ / /  / / / / / / /_/ / / /_/ /   / /       
    /_/    \____/_/  /_/ /_/ /_/\__,_/_/\__,_/   /_/        
                                                            """,
           """                                            
    ███████╗ ██╗     ██████╗██╗     ██╗     
    ██╔════╝███║    ██╔════╝██║     ██║     
    █████╗  ╚██║    ██║     ██║     ██║     
    ██╔══╝   ██║    ██║     ██║     ██║     
    ██║      ██║    ╚██████╗███████╗██║     
    ╚═╝      ╚═╝     ╚═════╝╚══════╝╚═╝     
                                            """,
           """                                                                                           
     _______                              _            __       ______  _        _____     
    (_______)                            | |          /  |     / _____)| |      (_____)    
     _____     ___    ____  ____   _   _ | |  ____   /_/ |    | /      | |         _       
    |  ___)   / _ \  / ___)|    \ | | | || | / _  |    | |    | |      | |        | |      
    | |      | |_| || |    | | | || |_| || |( ( | |    | |    | \_____ | |_____  _| |_     
    |_|       \___/ |_|    |_|_|_| \____||_| \_||_|    |_|     \______)|_______)(_____)    
                                                                                           
"""
           ]

DESCRIPTION = "\t\b\b\bFormula 1 CLI.\n\n"


class Banner:
    themes: List[int]
    banner: str

    def __init__(self, themes: Optional[List[int]] = None) -> None:
        if themes:
            self.themes = themes
        else:
            self.themes = [
                Fore.RED + Back.BLACK,
                Fore.BLACK + Back.WHITE,
                Fore.RED + Back.WHITE,
                Fore.WHITE + Back.BLACK,
            ]
        self.banner = random.choice(banners)

    def __str__(self):
        theme = random.choice(self.themes)
        style = random.choice([Style.DIM, Style.BRIGHT, Style.NORMAL])
        reset = Style.RESET_ALL

        return theme + self.banner + style + reset

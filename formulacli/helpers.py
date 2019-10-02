import os
import sys


def clear_screen() -> None:
    if sys.platform in ["linux", "linux2", "darwin"]:
        os.system("clear")
    elif sys.platform == "win32":
        os.system("cls")
    else:
        print("\n"*50)


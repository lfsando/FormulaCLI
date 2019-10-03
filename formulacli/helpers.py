from time import perf_counter
from os import system
from sys import platform


def clear_screen() -> None:
    if platform in ["linux", "linux2", "darwin"]:
        system("clear")
    elif platform == "win32":
        system("cls")
    else:
        print("\n" * 50)


class Timer:
    def __init__(self) -> None:
        self.t1: float = 0

    def __enter__(self):
        self.t1 = perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t2 = perf_counter()

        print(f"... took {round((self.t2 - self.t1), 2)} second(s)")

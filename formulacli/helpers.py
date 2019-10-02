import time
import os
import sys


def clear_screen() -> None:
    if sys.platform in ["linux", "linux2", "darwin"]:
        os.system("clear")
    elif sys.platform == "win32":
        os.system("cls")
    else:
        print("\n" * 50)


class Timer:
    def __init__(self) -> None:
        self.t1: float = 0

    def __enter__(self):
        self.t1 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t2 = time.perf_counter()

        print(f"... took {round((self.t2 - self.t1), 2)} second(s)")

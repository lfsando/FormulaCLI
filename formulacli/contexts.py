from __future__ import annotations

import sys
from collections import namedtuple
from datetime import datetime
from textwrap import TextWrapper
from typing import List, Dict, Any, Union, Optional, Type, Tuple

from PIL import Image
from colorama import Fore, Style, Back
from pandas import DataFrame, Series
from urllib3 import HTTPResponse

from formulacli.banners import Banner, DESCRIPTION
from formulacli.drivers import fetch_drivers, fetch_driver
from formulacli.exceptions import ExitException
from formulacli.html_handlers import get_response
from formulacli.img_to_ascii import convert
from formulacli.news import fetch_top_stories
from formulacli.result_tables import fetch_results

if sys.platform in ['linux', 'linux2', 'darwin']:
    from getch import getch as read_key
elif sys.platform == 'win32':
    from msvcrt import getch as read_key

Command = namedtuple("Command", ['cmd', 'label'])
Option = namedtuple("Option", ['opt', 'label'])
Message = namedtuple("Message", ['msg', 'type'])

BANNER = Banner()


class Context:
    history: List[Any] = []
    messages: List[Message] = []
    block_render: bool = True

    def __init__(self) -> None:
        self.state: Dict[str, Any] = {
            'name': "context",
            'next_ctx': self,
            'next_ctx_args': {},
            'command': '',
            'custom_commands': [],
            'menu_options': [],
            'show_banner': False,
            'string_input': False
        }

    def __str__(self):
        return self.state['name']

    def render(self) -> None:
        print(self)
        if self.state['show_banner']:
            print(self.banner)
        self.show_options()
        self.event()
        print()
        self.show_messages()
        print("Press h for help.")

        self.state['command'] = cmd = self.get_commands()

        if cmd.lower() in ['q', 'quit', 'exit']:
            raise ExitException
        elif cmd.lower() in ['m', 'menu']:
            self.state['next_ctx'] = MainContext
            self.state['next_ctx_args'] = {}
            return
        elif cmd.lower() in ['b', 'back']:
            try:
                Context.history.pop()
                self.state['next_ctx'] = Context.history[-1]
                self.state['next_ctx_args'] = {}
            except IndexError:
                self.state['next_ctx'] = MainContext
                self.state['next_ctx_args'] = {}
            return
        elif cmd.lower() in ['?', 'h', 'help']:
            self.show_help()
            self.state['next_ctx'] = Context.history[-1]
            return
        elif cmd.lower() == '\'':
            self.state['string_input'] = True

        self.action_handler()

    def action_handler(self) -> None:
        pass

    def event(self) -> None:
        pass

    def add_to_history(self) -> None:
        Context.history.append(self)

    def show_options(self) -> None:
        template = "[{opt}]  {label}"
        for option in self.state['menu_options']:
            self._pprint(template.format(opt=option.opt, label=option.label), margin=2)
        print()

    def show_messages(self) -> None:
        messages: List[Message] = Context.messages

        while messages:
            message: Message = messages.pop()
            if message.type == 'error':
                self._pprint(f"{Fore.RED}{message.msg}{Style.RESET_ALL}", margin=10)
            elif message.type == 'success':
                self._pprint(f"{Fore.LIGHTGREEN_EX}{message.msg}{Style.RESET_ALL}", margin=10)
            elif message.type == 'debug':
                self._pprint(f"{Fore.LIGHTCYAN_EX}{message.msg}{Style.RESET_ALL}", margin=10)

    def show_help(self) -> None:
        commands: List[Command] = []
        commands += [Command(cmd='\'', label="Write command")]
        commands += self.state['custom_commands']

        if len(Context.history) > 1:
            commands.append(Command(cmd='b', label="Back"))
        commands += [
            Command(cmd='h', label="Show commands"),
            Command(cmd='m', label="Menu"),
            Command(cmd='q', label="Quit")
        ]
        commands_df = DataFrame(commands, columns=["Commands", "?"]).to_string(index=False)
        Context.messages.append(Message(msg=commands_df, type='success'))

    @staticmethod
    def convert_image(
            url: str,
            brush: Optional[str] = None,
            colored: bool = False,
            ratio: Tuple[Union[float, int], Union[float, int]] = (1, 1),
            size: Optional[Tuple[int, int]] = None,
            crop_box: Optional[Tuple[int, int, int, int]] = None) -> str:

        im_bytes: HTTPResponse = get_response(url, b=True)
        im: Image = Image.open(im_bytes)
        if crop_box is not None:
            im = im.crop(crop_box)

        if ratio and size:
            im = im.resize(round(size[0] * ratio[0]), round(size[1] * ratio[1]))
        elif size:
            im = im.resize(size)
        elif ratio:
            im = im.resize((round(im.size[0] * ratio[0]), round(im.size[1] * ratio[1])))

        return convert(im, colored=colored, brush=brush)

    def get_commands(self) -> str:
        cmd: str = ''
        try:
            if self.state['string_input']:
                cmd = str(input(">> ")).strip()
                self.state['string_input'] = False
            else:
                try:
                    cmd = read_key()
                    if isinstance(cmd, bytes):
                        cmd = cmd.decode()
                except UnicodeDecodeError:
                    cmd = ""
        except EOFError:
            Context.messages.append(Message(msg="Invalid Command", type='error'))
        return cmd

    @property
    def banner(self):
        return str(BANNER) + "\n" + DESCRIPTION

    @staticmethod
    def _pprint(text, margin=10, end="\n"):
        for line in text.split('\n'):
            print(Style.RESET_ALL + " " * margin + line, end=end)


class MainContext(Context):

    def __init__(self) -> None:
        super().__init__()
        self.state.update({
            'name': "Main Menu",
            'next_ctx': self,
            'custom_commands': [
                Command(cmd='NUMBER', label="Select Option"),
            ],
            'menu_options': [
                Option(opt=1, label="Driver Standing"),
                Option(opt=2, label="Constructor Standing"),
                Option(opt=3, label="Races Results"),
                Option(opt=4, label="Fastest Laps"),
                Option(opt=5, label="Drivers"),
                Option(opt=6, label="Latest News"),
            ],
            'show_banner': True,
            'tables': [
                'drivers', 'team', 'races', 'fastest-laps'
            ],
        })

    def action_handler(self) -> None:
        try:
            cmd: int = int(self.state['command'])
        except ValueError:
            Context.messages.append(Message(msg="Invalid Command", type='error'))
            return
        if cmd in [1, 2, 3, 4]:
            self.state['next_ctx'] = ResultTableContext
            self.state['next_ctx_args'] = {"table_for": self.state["tables"][cmd - 1]}
        elif cmd == 5:
            self.state['next_ctx'] = DriversContext
            self.state['next_ctx_args'] = {}
        elif cmd == 6:
            self.state['next_ctx'] = NewsListContext
            self.state['next_ctx_args'] = {}


class ResultTableContext(Context):
    def __init__(self, table_for: str,
                 table: Optional[DataFrame] = None,
                 year: Optional[int] = None,
                 title: str = "") -> None:
        super().__init__()

        self.state.update({
            'name': table_for.replace("-", " ").title(),
            'next_ctx': self,
            'custom_commands': [
                Command(cmd='y:YEAR', label="Change Season"),
            ],
            'for': table_for,
            'year': year if year else datetime.now().year,
            'table': table,
            'title': title
        })
        if self.state['table'] is None:
            self._fetch_table()

    def event(self) -> None:
        table: str = self.state['table'].to_string(index=False)
        self._pprint(self.title, 35)
        self._pprint(table, 10)
        print()

    def action_handler(self) -> None:
        cmd: str = self.state['command']
        if cmd.lower().startswith("y:"):
            year: int = int(cmd.split(':')[1])
            self.state['next_ctx'] = ResultTableContext
            self.state['next_ctx_args'] = {
                'table_for': self.state['for'],
                'year': year,
                'table': None
            }
            Context.messages.append(Message(msg=f"Season changed to {year}", type='success'))

    def _fetch_table(self) -> None:
        try:
            table: DataFrame = fetch_results(self.state['for'], self.state['year'])
        except ValueError:
            self.state['year'] = datetime.now().year
            table = fetch_results(self.state['for'], self.state['year'])
            Context.messages.append(
                Message(msg=f"Invalid Season. [1950-{self.state['year']}]", type="error")
            )
        self.state['table'] = table

    @property
    def title(self) -> str:
        if self.state["title"]:
            return self.state["title"]

        titles: Dict[str, str] = {
            "drivers": "Drivers Championship",
            "team": "Constructor Championship",
            "races": "Race Results",
            "fastest-laps": "DHL Fastest Lap Award"
        }
        year: int = self.state["year"]
        return f"{year} {titles[self.state['for']]}\n"


class DriversContext(Context):
    def __init__(self,
                 drivers: Optional[DataFrame] = None) -> None:
        super().__init__()
        self.state.update({
            'name': "Drivers",
            'next_ctx': self,
            'custom_commands': [
                Command(cmd='INDEX', label="Select Driver"),
            ],
            'drivers': drivers,
        })

    def event(self) -> None:
        drivers: Optional[DataFrame] = self.state['drivers']
        if drivers is None:
            drivers = fetch_drivers()
            drivers.index += 1
            self.state["drivers"] = drivers
        self._pprint("Drivers\n", 30)
        self._pprint(drivers[["NAME", "NUMBER", "TEAM"]].to_string(), 10)
        print("\n")

    def action_handler(self) -> None:
        cmd: str = self.state['command']
        if cmd and cmd.isdecimal():
            try:
                index: int = int(cmd) - 1
                drivers: DataFrame = self.state["drivers"]
                driver: Series = drivers.iloc[index, :]
                self.state['next_ctx'] = DriverContext
                self.state['next_ctx_args'] = {
                    'driver': driver,
                    'driver_index': index,
                    'drivers': drivers
                }
            except IndexError:
                Context.messages.append(Message(msg="Invalid Driver Index", type="error"))


class DriverContext(Context):
    drivers_history: Dict[int, Context] = {}

    def __init__(self,
                 driver: Union[Series, Dict[str, str]],
                 driver_index: int,
                 drivers: DataFrame) -> None:
        super().__init__()
        self.state.update({
            'name': driver['NAME'],
            'next_ctx': self,
            'custom_commands': [
                Command(cmd='bio', label="Read Bio"),
                Command(cmd='d', label="Next Driver"),
                Command(cmd='a', label="Previous Driver"),
            ],
            'driver': driver,
            'portrait': None,
            'info': None,
            'index': driver_index,
            'drivers': drivers,
            'max_drivers': len(drivers) - 1,
        })
        DriverContext.drivers_history[driver_index] = self

        header = Back.LIGHTWHITE_EX
        driver_names = list(drivers['NAME'])
        for name in driver_names:
            if name == driver['NAME']:
                header += Fore.RED
                header += Back.WHITE
                header += name.split(' ')[-1]
                header += Back.LIGHTWHITE_EX
                header += Fore.RESET
            else:
                header += Fore.LIGHTBLACK_EX
                header += Style.DIM
                header += name.split(' ')[-1]
                header += Fore.RESET
            header += "  "
        else:
            header += Back.RESET
        self.header = header
        self.reset = True  # needs fixing

    def event(self) -> None:
        self._pprint(self.header + "\n", margin=2)

        portrait: Optional[str] = self.state['portrait']
        if portrait is None or self.reset:
            portrait = self.convert_image(url=self.state['driver']['IMG'],
                                          # size=(30, 20),
                                          ratio=(0.45, 0.22),
                                          crop_box=(105, 5, 215, 120)
                                          )
            self.reset = False
            self.state['portrait'] = portrait
        self._pprint(portrait, 7)

        driver: Union[Dict[str, str]] = dict(self.state['driver'])
        driver_info: Optional[Dict[str, str]] = self.state['info']
        if driver_info is None:
            driver_info = fetch_driver(driver['URL'])
            self.state['info'] = driver_info
        driver.update(driver_info)

        margin: int = 30
        for label, value in driver.items():
            if label not in ['BIO', 'URL', 'IMG']:
                row = label.title() + ":" + str(" " * (margin - len(label))) + value
                self._pprint(row, 2)
        print()

    def action_handler(self) -> None:
        cmd: str = self.state['command']

        if cmd.lower() == 'bio':
            self.state['next_ctx'] = TextContext
            self.state['next_ctx_args'] = {'text': self.state['info']['BIO']}

        elif cmd.lower() in ['d', 'a']:
            drivers = self.state['drivers']
            driver_idx = self.state['index']
            next_idx = driver_idx + 1 if cmd.lower() == 'd' else driver_idx - 1

            if next_idx > self.state['max_drivers']:
                next_idx = 0
            elif next_idx < 0:
                next_idx = self.state['max_drivers']

            next_driver: Union[Type[DriverContext], Series] = \
                DriverContext.drivers_history.get(next_idx, drivers.iloc[next_idx, :])

            if isinstance(next_driver, DriverContext):
                self.state['next_ctx'] = next_driver
                self.state['next_ctx_args'] = {}
            else:
                self.state['next_ctx'] = DriverContext
                self.state['next_ctx_args'] = {
                    'driver': next_driver,
                    'driver_index': next_idx,
                    'drivers': drivers
                }


class NewsListContext(Context):
    def __init__(self, articles: Optional[DataFrame] = None) -> None:
        super().__init__()
        self.state.update({
            'name': 'News List',
            'custom_commands': [
                Command(cmd='NUMBER', label="Select article"),
            ],
            'articles': articles if articles else fetch_top_stories(img_size=9),
            'headlines': []
        })

    def event(self) -> None:
        # TODO
        headlines = self.state['headlines']
        if headlines:
            for headline in headlines:
                print(headline)
        else:
            stories: DataFrame = self.state['articles']
            for i, story in stories.iterrows():
                headline = self.article_headline(story, i + 1)
                print(headline)
                headlines.append(headline)
        self.state['headlines'] = headlines

    def action_handler(self) -> None:
        try:
            index = int(self.state['command'])
            articles: DataFrame = self.state['articles']
            try:
                article: Series = articles.iloc[index - 1, :]
                Context.messages.append(Message(msg=article.to_string(), type="debug"))
            except IndexError:
                Context.messages.append(
                    Message(msg="Invalid index", type="error")
                )
        except ValueError:
            # other commands
            return

    @staticmethod
    def article_headline(story: Series, index: Optional[int] = None) -> str:
        headline: str = ""
        if 'main-story' in story.tags:
            headline += Style.BRIGHT
        headline += f"[{index}] [{story.tags[-1].upper()}]\t {story['headline']}" + Style.RESET_ALL
        headline = headline + '\n'

        return headline


class TextContext(Context):
    def __init__(self, text: str, width: int = 80) -> None:
        super().__init__()
        self.state.update({
            'name': 'Text',
            'next_ctx': self,
            'text': text,
            'width': width
        })

    def event(self) -> None:
        wrapper: TextWrapper = TextWrapper(width=self.state['width'])
        word_list: List[str] = wrapper.wrap(text=self.state['text'])
        for element in word_list:
            self._pprint(element, 3)
        print()


ContextType = Union[
    Type[Context],
    Context,
    Type[MainContext],
    MainContext,
    Type[ResultTableContext],
    ResultTableContext,
    Type[DriversContext],
    DriversContext,
    Type[DriverContext],
    DriverContext,
    Type[NewsListContext],
    NewsListContext,
    Type[TextContext],
    TextContext
]

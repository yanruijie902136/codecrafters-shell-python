import readline
from typing import NoReturn

from .autocomplete import Autocompleter
from .command import execute
from .scanner import Scanner
from .parser import Parser


class Shell:
    def __init__(self, prompt: str = "$ ") -> None:
        self._prompt = prompt
        self._autocompleter = Autocompleter()
        self._scanner = Scanner()
        self._parser = Parser()

    def start(self) -> NoReturn:
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self._autocompleter.complete)

        while True:
            line = input(self._prompt)
            tokens = self._scanner.scan(line)
            # print(tokens)
            command = self._parser.parse(tokens)
            # print(command)
            execute(command)

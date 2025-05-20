import os
import readline
import shlex
import shutil
import subprocess
import sys
from typing import NoReturn


def get_all_executables() -> set[str]:
    executables = set()

    path_env = os.getenv("PATH")
    if path_env is None:
        return executables

    for d in path_env.split(":"):
        try:
            names = os.listdir(d)
        except FileNotFoundError:
            continue

        for name in names:
            path = os.path.join(d, name)
            if os.path.isfile(path) and os.access(path, os.X_OK):
                executables.add(name)

    return executables


BUILTINS = set(["cd", "echo", "exit", "pwd", "type"])


class Completer:
    def __init__(self) -> None:
        self._candidates = BUILTINS.union(get_all_executables())

    def complete(self, text: str, state: int) -> str | None:
        if state == 0:
            self._matches = [s for s in self._candidates if s.startswith(text)]

        if state >= len(self._matches):
            return None
        elif len(self._matches) == 1:
            return self._matches[0] + " "
        else:
            return self._matches[state]


def execute_cd(arguments: list[str]) -> None:
    destination = os.path.expanduser(arguments[1])
    try:
        os.chdir(destination)
    except FileNotFoundError:
        sys.stderr.write(f"cd: {destination}: No such file or directory\n")


def execute_echo(arguments: list[str]) -> None:
    sys.stdout.write(" ".join(arguments[1:]) + "\n")


def execute_exit(arguments: list[str]) -> NoReturn:
    sys.exit(int(arguments[1]))


def execute_pwd(arguments: list[str]) -> None:
    sys.stdout.write(os.getcwd() + "\n")


def is_builtin(command_name: str) -> bool:
    return command_name in ["cd", "echo", "exit", "pwd", "type"]


def execute_type(arguments: list[str]) -> None:
    for command_name in arguments[1:]:
        if is_builtin(command_name):
            sys.stdout.write(f"{command_name} is a shell builtin\n")
        elif (path := shutil.which(command_name)) is not None:
            sys.stdout.write(f"{command_name} is {path}\n")
        else:
            sys.stdout.write(f"{command_name}: not found\n")


def execute(arguments: list[str]) -> None:
    if not arguments:
        return

    command_name = arguments[0]
    match command_name:
        case "cd":
            execute_cd(arguments)
        case "echo":
            execute_echo(arguments)
        case "exit":
            execute_exit(arguments)
        case "pwd":
            execute_pwd(arguments)
        case "type":
            execute_type(arguments)
        case _:
            try:
                subprocess.run(arguments)
            except FileNotFoundError:
                sys.stderr.write(f"{command_name}: command not found\n")


def main() -> None:
    readline.parse_and_bind("tab: complete")
    readline.set_completer(Completer().complete)

    while True:
        sys.stdout.write("$ ")
        arguments = shlex.split(input(), posix=True)
        execute(arguments)


if __name__ == "__main__":
    main()

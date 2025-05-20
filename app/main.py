import os
import shutil
import subprocess
import sys
from typing import NoReturn


def execute_echo(arguments: list[str]) -> None:
    sys.stdout.write(" ".join(arguments[1:]) + "\n")


def execute_exit(arguments: list[str]) -> NoReturn:
    sys.exit(int(arguments[1]))


def execute_pwd(arguments: list[str]) -> None:
    sys.stdout.write(os.getcwd() + "\n")


def is_builtin(command_name: str) -> bool:
    return command_name in ["echo", "exit", "pwd", "type"]


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
    while True:
        sys.stdout.write("$ ")
        arguments = input().split()
        execute(arguments)


if __name__ == "__main__":
    main()

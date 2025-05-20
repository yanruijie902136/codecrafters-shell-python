import sys
from typing import NoReturn


def execute_exit(arguments: list[str]) -> NoReturn:
    sys.exit(int(arguments[1]))


def execute(arguments: list[str]) -> None:
    if not arguments:
        return

    command_name = arguments[0]
    match command_name:
        case "exit":
            execute_exit(arguments)
        case _:
            sys.stderr.write(f"{command_name}: command not found\n")


def main() -> None:
    while True:
        sys.stdout.write("$ ")
        arguments = input().split()
        execute(arguments)


if __name__ == "__main__":
    main()

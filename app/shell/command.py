import os
import readline
import shutil
import subprocess
import sys
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from dataclasses import dataclass


BUILTINS = set(["cd", "echo", "exit", "history", "pwd", "type"])


def get_all_executables() -> set[str]:
    executables = set()

    path_env = os.getenv("PATH")
    if path_env is None:
        return executables

    for directory in path_env.split(":"):
        try:
            names = os.listdir(directory)
        except FileNotFoundError:
            continue

        for name in names:
            path = os.path.join(directory, name)
            if os.path.isfile(path) and os.access(path, os.X_OK):
                executables.add(name)

    return executables


@dataclass(frozen=True)
class Command:
    arguments: list[str]
    redir_stdout: tuple[str, str] | None
    redir_stderr: tuple[str, str] | None


def _execute_cd(arguments: list[str]) -> None:
    destination = os.path.expanduser(arguments[1])
    try:
        os.chdir(destination)
    except FileNotFoundError:
        sys.stderr.write(f"cd: {destination}: No such file or directory\n")


def _execute_echo(arguments: list[str]) -> None:
    sys.stdout.write(" ".join(arguments[1:]) + "\n")


def _execute_exit(arguments: list[str]) -> None:
    sys.exit(int(arguments[1]))


def _execute_history(arguments: list[str]) -> None:
    if len(arguments) > 1 and arguments[1] == "-r":
        readline.read_history_file(arguments[2])
        return
    elif len(arguments) > 1 and arguments[1] == "-w":
        readline.write_history_file(arguments[2])
        return

    nitems = readline.get_current_history_length()
    n = int(arguments[1]) if len(arguments) > 1 else nitems
    for i in range(nitems + 1 - n, nitems + 1):
        line = readline.get_history_item(i)
        sys.stdout.write(f"{i:>5}  {line}\n")


def _execute_pwd(arguments: list[str]) -> None:
    sys.stdout.write(os.getcwd() + "\n")


def _execute_type(arguments: list[str]) -> None:
    for command_name in arguments[1:]:
        if command_name in BUILTINS:
            sys.stdout.write(f"{command_name} is a shell builtin\n")
        elif (path := shutil.which(command_name)) is not None:
            sys.stdout.write(f"{command_name} is {path}\n")
        else:
            sys.stdout.write(f"{command_name}: not found\n")


def _execute(arguments: list[str]) -> None:
    match (command_name := arguments[0]):
        case "cd":
            _execute_cd(arguments)
        case "echo":
            _execute_echo(arguments)
        case "exit":
            _execute_exit(arguments)
        case "history":
            _execute_history(arguments)
        case "pwd":
            _execute_pwd(arguments)
        case "type":
            _execute_type(arguments)
        case _:
            try:
                subprocess.run(arguments, stdout=sys.stdout, stderr=sys.stderr)
            except FileNotFoundError:
                sys.stderr.write(f"{command_name}: command not found\n")


def execute_command(command: Command) -> None:
    with ExitStack() as stack:
        if command.redir_stdout is not None:
            f = open(*command.redir_stdout)
            stack.enter_context(f)
            stack.enter_context(redirect_stdout(f))

        if command.redir_stderr is not None:
            f = open(*command.redir_stderr)
            stack.enter_context(f)
            stack.enter_context(redirect_stderr(f))

        _execute(command.arguments)


def execute_commands(commands: list[Command]) -> None:
    if not commands:
        return
    elif len(commands) == 1:
        execute_command(commands[0])
        return

    rfd, wfd, prev_rfd = -1, -1, -1
    for i, command in enumerate(commands):
        if i < len(commands) - 1:
            rfd, wfd = os.pipe()

        if os.fork() == 0:
            if i > 0:
                os.dup2(prev_rfd, 0)
                os.close(prev_rfd)

            if i < len(commands) - 1:
                os.dup2(wfd, 1)
                os.close(wfd)

            execute_command(command)
            sys.exit(0)

        if i > 0:
            os.close(prev_rfd)

        if i < len(commands) - 1:
            os.close(wfd)

        prev_rfd = rfd

    for i in range(len(commands)):
        os.wait()

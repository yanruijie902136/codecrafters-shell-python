import sys


def main() -> None:
    while True:
        sys.stdout.write("$ ")
        line = input()
        sys.stderr.write(f"{line}: command not found\n")


if __name__ == "__main__":
    main()

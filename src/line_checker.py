""" Line length checker. """
import argparse

from typing import List
from typing import Tuple


DEFAULT_LINE_LENGTH = 80


class LineCheckerError(Exception):
    pass


def verify_filename(filename: str) -> bool:
    # TODO add more checks to verify the file
    if filename.rsplit(".")[-1] == "py":
        return True
    else:
        return False


def load_file(filename: str) -> List[str]:
    try:
        with open(filename, "r") as f:
            data = f.read()
    except FileNotFoundError:
        raise FileNotFoundError

    line_data = []
    for d in data.splitlines():
        line_data.append(d)
    return line_data


def checker(line_data: List[str]) -> List[Tuple[int, int]]:
    fail_lines = []
    for i, line in enumerate(line_data):
        line_len = len(line)
        if line_len >= DEFAULT_LINE_LENGTH:
            fail_lines.append((i, line_len))
    return fail_lines


def build_summary(filename: str,
                  file_failed: str,
                  fail_lines: List[Tuple[int, int]]) -> str:

    summary = f"""
-------- Check completed --------
{filename}...[{file_failed}]

"""
    fail_summary = "Lines     length\n"
    for line in fail_lines:
        fail_summary += f"{line[0] + 1}         {line[1]}\n"

    summary += fail_summary
    summary += "------ END SUMMARY ------"
    return summary


def display_welcome() -> None:
    print("-------- Line Checker --------")
    print(f"          version")  # TODO add version here


def display_error() -> None:
    print("Error file not found or file is not a python file")
    print("Aborting")


def display_summary(summary: str) -> None:
    print(summary)


def argument_parsing(argv: list = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Filename to check.")
    return parser.parse_args(argv)


def main(argv: list = None) -> int:
    args = argument_parsing(argv)

    display_welcome()
    if verify_filename(args.file):
        try:
            file_data = load_file(args.file)
        except FileNotFoundError as e:
            print(e)
            return 1
        else:
            fail_lines = checker(file_data)
            if fail_lines:
                file_failed = "FAIL"
            else:
                file_failed = "PASSED"
            summary = build_summary(args.file, file_failed, fail_lines)
            display_summary(summary)
            return 0

    else:
        display_error()
        return 1


if __name__ == "__main__":
    exit(main())

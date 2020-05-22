""" Line length checker. """
import argparse
import shutil
import time


from typing import List
from typing import Tuple


DEFAULT_LINE_LENGTH = 80
SEP = "-"


class LineCheckerError(Exception):
    pass


class ElapseTime:
    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def get_elapse_time(self):
        return self.end_time - self.start_time


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
    except FileNotFoundError as e:
        raise FileNotFoundError(e)

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


def display_check_completed(elapse_time: float) -> None:
    terminal_col, _ = shutil.get_terminal_size()
    title = f"1 file checked in {elapse_time:.2f} s"
    title_sep = SEP * int((terminal_col/2) - 1 - len(title)/2)
    completed_line = f"{title_sep} {title} {title_sep}"
    print(completed_line)


def display_summary(filename: str,
                    file_failed: str,
                    fail_lines: List[Tuple[int, int]]) -> None:
    dot = "."
    terminal_col, _ = shutil.get_terminal_size()
    # title = "Summary"
    # title_sep = SEP * int((terminal_col/2) - 1 - len(title)/2)
    # summary_line = f"{title_sep} {title} {title_sep}"

    dot_fill = dot * (terminal_col - len(filename) - len(file_failed) - 5)
    file_line = f"{filename}{dot_fill}[{file_failed}]"

    print()
    # print(summary_line)
    print(file_line)
    if fail_lines:
        print("      Line     Length")
        for line in fail_lines:
            print(f"      {line[0] + 1}        {line[1]}")


def display_welcome() -> None:
    # use _ for terminal_lines
    terminal_col, terminal_lines = shutil.get_terminal_size()
    title = "Line Checker"
    title_sep = SEP * int((terminal_col/2) - 1 - len(title)/2)
    title_line = f"{title_sep} {title} {title_sep}"

    print(title_line)
    print("version: 0.0.0")
    print()


def display_error(error_message) -> None:
    print(f"Error: {error_message}")
    print()
    print("Aborting")


def argument_parsing(argv: list = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Filename to check.")
    return parser.parse_args(argv)


def main(argv: list = None) -> int:
    args = argument_parsing(argv)

    elapse_time = ElapseTime()
    elapse_time.start()
    display_welcome()
    if verify_filename(args.file):
        try:
            file_data = load_file(args.file)
        except FileNotFoundError:
            display_error("File is not found")
            return 1
        else:
            fail_lines = checker(file_data)
            if fail_lines:
                file_failed = "FAIL"
            else:
                file_failed = "PASSED"

            elapse_time.stop()
            display_check_completed(elapse_time.get_elapse_time())
            display_summary(args.file, file_failed, fail_lines)
            return 0

    else:
        display_error("File is not "
                      "a check-able file")
        return 1


if __name__ == "__main__":
    exit(main())

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
    def __init__(self) -> None:
        self.start_time = 0.0
        self.end_time = 0.0

    def start(self) -> None:
        self.start_time = time.time()

    def stop(self) -> None:
        self.end_time = time.time()

    def elapse_time(self) -> float:
        return self.end_time - self.start_time


class Display:
    def __init__(self,
                 show_elapse_time: bool,
                 display_color: bool = False) -> None:
        if display_color:
            pass
            self.red = "\033[1;31m"
            self.green = "\033[1;32m"
            self.reset_color = "\033[0m"
        else:
            self.red = ""
            self.green = ""
            self.reset_color = ""

        self.script_name = "Line Checker"
        self.dot = "."
        self.failed = f"{self.red}Failed{self.reset_color}"
        self.passed = f"{self.green}Passed{self.reset_color}"
        self.show_elapse_time = show_elapse_time

    def welcome(self) -> None:
        print(self.script_name)

    def summary(self, num_checked: int,
                num_failed: int,
                elapse_time: float) -> None:
        if self.show_elapse_time:
            elapse_time_str = f"  in {elapse_time:.2f}s"
        else:
            elapse_time_str = ""
        string = f"{num_checked} files checked"
        if num_checked == 0:
            state = ""
        elif num_failed == 0:
            state = f": {self.passed}"
        elif num_failed == num_checked:
            state = f": {self.failed}"
        else:
            state = f": {num_checked - num_failed} {self.passed}, "
            state += f"{num_failed} {self.failed}"
        print(f"{string}{state}{elapse_time_str}")

    def failed_details(self, filename: str,
                       fail_lines: List[Tuple[int, int]]
                       ) -> None:
        print(f"{filename}")
        for line in fail_lines:
            print(f"  line: {line[0] + 1}  -  length: {line[1]}")

    def error(self, msg: str) -> None:
        print(f"{self.red}{msg}{self.reset_color}")


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


def checker(line_data: List[str], line_length: int) -> List[Tuple[int, int]]:
    fail_lines = []
    for i, line in enumerate(line_data):
        line_len = len(line)
        if line_len > line_length:
            fail_lines.append((i, line_len))
    return fail_lines


def argument_parsing(argv: list = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Filename to check.")
    parser.add_argument("-l", "--line_length", action="store", type=int,
                        default=DEFAULT_LINE_LENGTH, help="max line length")
    parser.add_argument("-E", "--elapse_time", action="store_true",
                        help="elapse time in seconds to run check")
    parser.add_argument("--no_color", dest="color", action="store_false",
                        help="turn off color output")
    return parser.parse_args(argv)


def main(argv: list = None) -> int:
    elapse_timer = ElapseTime()
    args = argument_parsing(argv)
    display = Display(args.elapse_time, args.color)

    elapse_timer.start()
    display.welcome()

    fail_count = 0
    check_count = 1
    if verify_filename(args.file):
        try:
            file_data = load_file(args.file)
        except FileNotFoundError:
            elapse_timer.stop()
            display.error("Error: File not found")
            display.summary(0, 0, elapse_timer.elapse_time())
            return 1
        else:
            fail_lines = checker(file_data, args.line_length)
            if fail_lines:
                fail_count += 1

            elapse_timer.stop()
            display.summary(check_count, fail_count, elapse_timer.elapse_time())
            if fail_count >= 1:
                display.failed_details(args.file, fail_lines)
            return 0

    else:
        elapse_timer.stop()
        display.summary(0, 0, elapse_timer.elapse_time())
        return 1


if __name__ == "__main__":
    exit(main())

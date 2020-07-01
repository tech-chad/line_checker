""" Line length checker. """
import argparse
import os
import sys
import time

from identify import identify  # type: ignore

from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata

version = importlib_metadata.version("line-checker")

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
                 display_color: bool = False,
                 quiet_mode: bool = False) -> None:
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
        self.quiet_mode = quiet_mode

    def welcome(self) -> None:
        if not self.quiet_mode:
            print(self.script_name)

    def summary(self, num_checked: int,
                num_failed: int,
                elapse_time: float) -> None:

        if self.quiet_mode and num_failed == 0:
            return None

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


def save_results_to_file(file_list: List[str], fail_list: list):
    filename = f"line_checker_out{time.strftime('%Y-%m-%d-%H%M%S')}"
    data = ""
    data += "line checker\n"
    if fail_list:
        data += f"{len(file_list)} file checked: failed\n"
        for fail_file, fail_data in fail_list:
            data += f"{fail_file}\n"
            for line, length in fail_data:
                data += f"  line {line + 1} - length: {length}\n"
    else:
        data += f"{len(file_list)} file checked: passed\n"
    with open(filename, "w") as f:
        f.write(data)


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


def discovery(path: str, tags_to_find: List[str],) -> List[str]:
    # look at directory or file at path, get tags for each file save
    # save wanted file (path) to a list and return the list
    files_to_check = []
    if os.path.isdir(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            tags = identify.tags_from_path(item_path)
            for tf in tags_to_find:
                if tf in tags:
                    files_to_check.append(item_path)
    else:
        tags = identify.tags_from_path(path)
        for tf in tags_to_find:
            if tf in tags:
                files_to_check.append(path)
    return files_to_check


def checker(line_data: List[str], line_length: int) -> List[Tuple[int, int]]:
    fail_lines = []
    for i, line in enumerate(line_data):
        line_len = len(line)
        if line_len > line_length:
            fail_lines.append((i, line_len))
    return fail_lines


def argument_parsing(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Filename to check.")
    parser.add_argument("-l", dest="line_length", action="store", type=int,
                        default=DEFAULT_LINE_LENGTH, help="max line length")
    parser.add_argument("-E", "--elapse_time", action="store_true",
                        help="elapse time in seconds to run check")
    parser.add_argument("-q", dest="quiet_mode", action="store_true",
                        help="Quiet mode. No output unless fail or error")
    parser.add_argument("-S", dest="save_to_file", action="store_true",
                        help="Save output to file")
    parser.add_argument("--no_color", dest="color", action="store_false",
                        help="turn off color output")
    parser.add_argument("--version", action="version",
                        version=f"Version: {version}")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    elapse_timer = ElapseTime()
    args = argument_parsing(argv)
    display = Display(args.elapse_time, args.color, args.quiet_mode)

    elapse_timer.start()
    display.welcome()

    fail_count = 0
    fails = []
    check_count = 0

    try:
        files_to_check = discovery(args.file, ["python"])
    except ValueError:
        display.error("Error file not found during discovery")
        elapse_timer.stop()
        display.summary(0, 0, elapse_timer.elapse_time())
        return 1
    else:
        for file in files_to_check:
            file_data = load_file(file)
            fail_lines = checker(file_data, args.line_length)
            check_count += 1
            if fail_lines:
                fail_count += 1
                fails.append((file, fail_lines))
        else:
            elapse_timer.stop()
            display.summary(check_count, fail_count, elapse_timer.elapse_time())
            if fail_count > 0:
                for fail_file in fails:
                    display.failed_details(fail_file[0], fail_file[1])
            if args.save_to_file:
                save_results_to_file(files_to_check, fails)
            return 0


if __name__ == "__main__":
    exit(main())

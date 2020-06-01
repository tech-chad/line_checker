import pytest

from line_checker import line_checker


def test_load_file(make_test_file):
    file_contents = "one line text file"
    filename = "test.txt"
    test_file = make_test_file(filename, file_contents)

    result = line_checker.load_file(test_file)
    assert len(result) == 1
    assert result[0] == file_contents


def test_load_file_small_file(make_test_file):
    file_contents = """# Line 1
# line 2

def foo():
    return 'bar'
"""
    filename = "test.py"
    test_file = make_test_file(filename, file_contents)

    result = line_checker.load_file(test_file)
    assert len(result) == 5
    assert result[1] == "# line 2"
    assert result[4] == "    return 'bar'"


def test_load_file_no_lines_empty_file(make_test_file):
    test_file = make_test_file("foo.py", "")
    result = line_checker.load_file(test_file)
    assert len(result) == 0
    assert result == []


def test_load_file_not_found(tmpdir):
    t = tmpdir.join("foo.py")
    with pytest.raises(FileNotFoundError):
        line_checker.load_file(t.strpath)


def test_checker_no_lines():
    line_data = []
    result = line_checker.checker(line_data, line_checker.DEFAULT_LINE_LENGTH)
    assert len(result) == 0
    assert result == []


def test_checker_no_fail_lines():
    line_data = [
        "# first comment line",
        "import time",
        "",
        "",
        "def main() -> None:",
        "    time.sleep(1)",
        "",
        "",
        "if __name__ == '__main__':",
        "    main()",
        "",
    ]
    result = line_checker.checker(line_data, line_checker.DEFAULT_LINE_LENGTH)
    assert len(result) == 0
    assert result == []


def test_checker_one_fail_line():
    # lest max line length 80
    line_data = [
        "# first comment line",
        "import time",
        "",
        "",
        "def main() -> None:",
        "    time.sleep(1)  # this is a comment line. A really long comment "
        "line over the test length of a line",
        "",
        "",
        "if __name__ == '__main__':",
        "    main()",
        "",
    ]
    result = line_checker.checker(line_data, line_checker.DEFAULT_LINE_LENGTH)
    assert len(result) == 1
    assert result == [(5, 102)]


def test_checker_three_fail_lines():
    # lest max line length 80
    line_data = [
        "# first comment line",
        "import time",
        "",
        "",
        "def main() -> None:",
        "    time.sleep(1)  # this is a comment line. A really long comment "
        "line over the test length of a line",
        "    print('this is a print.  printing a long line to test this out"
        " just a bit over 85",
        "",
        "",
        "if __name__ == '__main__':",
        "    main()  # this is a call to the main function.  the main function"
        " is where it is all at.  just call main()",
        "",
    ]
    result = line_checker.checker(line_data, line_checker.DEFAULT_LINE_LENGTH)
    assert len(result) == 3
    assert result == [(5, 102), (6, 85), (10, 110)]


@pytest.mark.parametrize("test_lengths, expected_len, expected_fails", [
    (90, 2, [(4, 123), (6, 92)]),
    (100, 1, [(4, 123)]),
    (124, 0, []),
    (123, 0, []),
    (122, 1, [(4, 123)]),
    (85, 3, [(4, 123), (6, 92), (10, 88)])

])
def test_checker_different_max_len(test_lengths, expected_len, expected_fails):
    # line 0: 42, line 4: 123, line 6: 92, line 10: 88
    line_data = [
        "# first comment line explaining the script",
        "import time",
        "",
        "",
        "def main(s: int) -> None:  # main function that takes in seconds as"
        " an int.  the seconds will be used in the sleep function",
        "    sleep(s)",
        "    print('Done sleeping and now exiting')  # this prints the text."
        " main returns after print",
        "",
        "",
        "if __name__ == '__main__':",
        "    # this is the entry point into the script and anything after this"
        " comment line runs.",
        "    main()",
        ""
    ]
    result = line_checker.checker(line_data, test_lengths)
    assert len(result) == expected_len
    assert result == expected_fails


def test_main_file_not_found(tmpdir, capsys):
    expected_cap = """Line Checker
\033[1;31mError file not found during discovery\033[0m
0 files checked\n"""
    td = tmpdir.join("foo.py")
    result = line_checker.main([td.strpath])
    captured_output = capsys.readouterr().out
    assert captured_output == expected_cap
    assert result == 1


def test_main_not_python_file(capsys, make_test_file):
    line_data = ["line 1 of a text file\n", "\n", "another line\n"]
    file_data = "".join(line_data)
    tf = make_test_file("foo.txt", file_data)

    expected_cap = "Line Checker\n0 files checked\n"
    result = line_checker.main([tf])
    captured_output = capsys.readouterr().out
    assert captured_output == expected_cap
    assert result == 0


@pytest.mark.parametrize("options, expected_cap", [
    pytest.param([], "Line Checker\n1 files checked: \033[1;32mPassed\033[0m\n",
                 id="with color"),
    pytest.param(["--no_color"], "Line Checker\n1 files checked: Passed\n",
                 id="no color"),
    pytest.param(
        ["-E"],
        "Line Checker\n1 files checked: \033[1;32mPassed\033[0m  in 0.00s\n",
        id="show elapse time"),
    pytest.param(["--no_color", "-E"],
                 "Line Checker\n1 files checked: Passed  in 0.00s\n",
                 id="show elapse time but no color"),
])
def test_main_one_file_passed(capsys, make_test_file, options, expected_cap):
    line_data = [
        "# first line is a comment\n",
        "import time\n",
        "\n",
        "\n",
        "def main():\n",
        "    print('hello')\n",
        "    sleep(1)\n",
        "    print('world')\n",
        "\n",
        "\n",
        "main()\n",
        "\n",
    ]
    file_data = "".join(line_data)
    tf = make_test_file("foo.py", file_data)

    # expected_cap = "Line Checker\n1 files checked: \033[1;32mPassed\033[0m\n"
    result = line_checker.main([tf] + options)
    captured_output = capsys.readouterr().out
    assert captured_output == expected_cap
    assert result == 0


def test_main_one_file_failed(capsys, make_test_file):
    line_data = [
        "# first line is a comment\n",
        "import time\n",
        "\n",
        "\n",
        "def main():  # this is the main function where everything runs in"
        " runs in this function when we call it\n",
        "    print('hello')\n",
        "    sleep(1)\n",
        "    print('world')\n",
        "\n",
        "\n",
        "main()\n",
        "\n",
    ]
    file_data = "".join(line_data)
    tf = make_test_file("foo.py", file_data)

    summary = "Line Checker\n1 files checked: \033[1;31mFailed\033[0m\n"
    details = f"{tf}\n  line: 5  -  length: 103\n"
    expected_capture = summary + details
    result = line_checker.main([tf])
    captured_output = capsys.readouterr().out
    assert captured_output == expected_capture
    assert result == 0


def test_main_multiple_files_no_check(capsys, make_temp_directory):
    td = make_temp_directory()
    td.add_empty_file("README.md")
    td.add_empty_file("foo.txt")
    td.add_empty_file("bar.c")
    td.add_empty_file("test")
    td.add_empty_file("data")
    td.add_directories_root(["tests"])
    test_dir = td.get_temp_directory()

    expected_cap = "Line Checker\n0 files checked\n"
    result = line_checker.main([test_dir])
    captured_output = capsys.readouterr().out
    assert captured_output == expected_cap
    assert result == 0


def test_main_multiple_files_passed(capsys, make_temp_directory):
    line_data = [
        "# first line is a comment\n",
        "\n",
        "\n",
        "def main():\n",
        "    print('hello world')\n",
        "\n",
        "\n",
        "main()\n",
        "\n",
    ]
    file_data = "".join(line_data)
    td = make_temp_directory()
    td.add_empty_file("README.md")
    td.add_file("foo.py", file_data)
    td.add_file("bar.py", file_data)
    td.add_empty_file("foobar.py")
    td.add_empty_file("test")
    td.add_empty_file("data")
    td.add_directories_root(["tests"])
    test_dir = td.get_temp_directory()

    expected_cap = "Line Checker\n3 files checked: \033[1;32mPassed\033[0m\n"
    result = line_checker.main([test_dir])
    captured_output = capsys.readouterr().out
    assert captured_output == expected_cap
    assert result == 0


def test_main_multiple_files_one_fail(capsys, make_temp_directory):
    line_data = [
        "# first line is a comment and someday this long line will be "
        " removed from this file\n",
        "\n",
        "\n",
        "def main():\n",
        "    print('hello world')\n",
        "\n",
        "\n",
        "# this is the main function call.  some more random stuff to fill "
        "this line with to get it over\n"
        "main()\n",
        "\n",
    ]
    file_data = "".join(line_data)
    td = make_temp_directory()
    td.add_empty_file("README.md")
    td.add_file("foo.py", file_data)
    td.add_file("bar.py", "# new file to add\nprint('hello world')\n\n")
    td.add_empty_file("foobar.py")
    td.add_empty_file("test")
    td.add_empty_file("data")
    td.add_directories_root(["tests"])
    test_dir = td.get_temp_directory()

    summary = "Line Checker\n3 files checked: 2 \033[1;32mPassed\033[0m,"
    summary += " 1 \033[1;31mFailed\033[0m\n"
    details = f"{test_dir + '/' + 'foo.py'}\n  line: 1  -  length: 84\n"
    details += f"  line: 8  -  length: 95\n"
    expected_capture = summary + details
    result = line_checker.main([test_dir])
    captured_output = capsys.readouterr().out
    assert captured_output == expected_capture
    assert result == 0


@pytest.mark.parametrize("length, details", (
    pytest.param([],
                 "  line: 1  -  length: 86\n  line: 5  -  length: 103\n",
                 id="normal"),

    pytest.param(["-l80"],
                 "  line: 1  -  length: 86\n  line: 5  -  length: 103\n",
                 id="-l80"),

    pytest.param(["-l90"],
                 "  line: 5  -  length: 103\n",
                 id="-l90"),

    pytest.param(["-l70"],
                 "  line: 1  -  length: 86\n  line: 5  -  length: 103\n"
                 "  line: 9  -  length: 74\n",
                 id="-l70"),
))
def test_main_line_length(make_test_file, capsys, length, details):
    line_data = [
        "# first line is a comment.  some more random stuff to say here"
        " but not going to say it\n",
        "import time\n",
        "\n",
        "\n",
        "def main():  # this is the main function where everything runs in"
        " runs in this function when we call it\n",
        "    print('hello')\n",
        "    sleep(1)\n",
        "    print('world')\n",
        "    print('print this string out to see what it looks like"
        "on screen to see\n"
        "\n",
        "\n",
        "main()\n",
        "\n",
    ]
    file_data = "".join(line_data)
    tf = make_test_file("foo.py", file_data)

    summary = "Line Checker\n1 files checked: \033[1;31mFailed\033[0m\n"
    details = f"{tf}\n{details}"
    expected_capture = summary + details
    result = line_checker.main([tf] + length)
    captured_output = capsys.readouterr().out
    assert captured_output == expected_capture
    assert result == 0


def test_main_line_length_pass(make_test_file, capsys):
    line_data = [
        "# first line is a comment.  some more random stuff to say here"
        " but not going to say it\n",
        "import time\n",
        "\n",
        "\n",
        "def main():  # this is the main function where everything runs in"
        " runs in this function when we call it\n",
        "    print('hello')\n",
        "    sleep(1)\n",
        "    print('world')\n",
        "    print('print this string out to see what it looks like"
        "on screen to see\n"
        "\n",
        "\n",
        "main()\n",
        "\n",
    ]
    file_data = "".join(line_data)
    tf = make_test_file("foo.py", file_data)
    expected_cap = "Line Checker\n1 files checked: \033[1;32mPassed\033[0m\n"
    # details = f"{tf}\n{details}"
    result = line_checker.main([tf, "-l105"])
    captured_output = capsys.readouterr().out
    assert captured_output == expected_cap
    assert result == 0

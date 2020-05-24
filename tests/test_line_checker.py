import pytest

from unittest import mock

from line_checker import line_checker


@pytest.fixture
def make_test_file(tmpdir):
    def _make_test_file(filename, file_contents):
        t = tmpdir.join(filename)
        t.write(file_contents)
        return t.strpath

    return _make_test_file


@pytest.mark.parametrize("test_names, expected_results", [
    ("test.py", True),
    ("dummpy.py", True),
    ("hello.py", True),
    ("test.txt", False),
    ("test", False),
    ("pytest", False),
    ("test.c", False),
])
def test_verify_filename(test_names, expected_results):
    result = line_checker.verify_filename(test_names)
    assert result == expected_results


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


def test_display_check_completed(capsys):
    line_checker.display_check_completed(0.22)
    captured_output = capsys.readouterr().out
    assert "1 file checked" in captured_output
    assert "0.22 s" in captured_output


def test_display_summary_passed(capsys):
    line_checker.display_summary("test.py", "PASSED", [])
    captured_output = capsys.readouterr().out
    assert "test.py" in captured_output
    assert "[PASSED]" in captured_output
    assert "Line" not in captured_output
    assert "Length" not in captured_output


def test_display_summary_failed(capsys):
    line_checker.display_summary("test.py", "FAIL", [(2, 85), (10, 90)])
    captured_output = capsys.readouterr().out
    assert "test.py" in captured_output
    assert "[FAIL]" in captured_output
    assert "Line" in captured_output
    assert "Length" in captured_output
    assert "3" in captured_output
    assert "85" in captured_output
    assert "11" in captured_output
    assert "90" in captured_output
    assert "10" not in captured_output


def test_display_welcome(capsys):
    line_checker.display_welcome()
    captured_output = capsys.readouterr().out
    assert "Line Checker" in captured_output
    assert "-" in captured_output
    assert "version:" in captured_output


def test_display_error(capsys):
    line_checker.display_error("error message")
    captured_output = capsys.readouterr().out
    assert "Error: error message" in captured_output
    assert "Aborting" in captured_output


def test_elapse_time_init():
    elapse_time = line_checker.ElapseTime()
    assert elapse_time.start_time == 0.0
    assert elapse_time.end_time == 0.0


def test_elapse_time_start():
    with mock.patch.object(line_checker.time, "time", return_value=1.0):
        elapse_time = line_checker.ElapseTime()
        elapse_time.start()
        assert elapse_time.start_time == 1.0


def test_elapse_time_end():
    elapse_time = line_checker.ElapseTime()
    with mock.patch.object(line_checker.time, "time", return_value=1.0):
        elapse_time.start()
    with mock.patch.object(line_checker.time, "time", return_value=3.5):
        elapse_time.stop()
    assert elapse_time.start_time == 1.0
    assert elapse_time.end_time == 3.5


def test_elapse_time_get():
    elapse_time = line_checker.ElapseTime()
    with mock.patch.object(line_checker.time, "time", return_value=1.0):
        elapse_time.start()
    with mock.patch.object(line_checker.time, "time", return_value=3.5):
        elapse_time.stop()
    result = elapse_time.get_elapse_time()
    assert result == 2.5


def test_argument_parsing_file():
    result = line_checker.argument_parsing(["test.py"])
    assert result.file == "test.py"


@pytest.mark.parametrize("test_args, expected_results", [
    (["test.py"], 80),
    (["test.py", "-l100"], 100),
    (["test.py", "--line_length", "75"], 75),
])
def test_argument_parsing_line_length(test_args, expected_results):
    result = line_checker.argument_parsing(test_args)
    assert result.line_length == expected_results


def test_argument_parsing_no_arguments():
    with pytest.raises(SystemExit):
        line_checker.argument_parsing([])


def test_argument_parsing_help(capsys):
    with pytest.raises(SystemExit):
        line_checker.argument_parsing(["-h"])
    captured_output = capsys.readouterr().out
    assert "usage" in captured_output


def test_main_display_elapse_time(make_test_file, capsys):
    test_file = make_test_file("test.py", "# line 1")
    with mock.patch.object(line_checker.ElapseTime,
                           "get_elapse_time",
                           return_value=2.5):
        line_checker.main([test_file])
    captured_output = capsys.readouterr().out
    assert "2.50 s" in captured_output


@pytest.mark.parametrize("test_len, exp_result", [
    ([], ["5        92", "8        104"]),
    (["-l100"], ["8        104"]),
    (["-l74"], ["5        92", "7        75", "8        104"])

])
def test_main_line_length_fail(make_test_file, capsys, test_len, exp_result):
    file_contents = """# first line comment
import time


def main(seconds: int) -> None:  # this is the main function that takes in seconds as an int
    print("before sleep")
    time.sleep(seconds)  # this is the sleep function from the time module.
    print("This is after the sleep function.  You can see the delay between the first print and this one


if __main__ == "__name__":
    main()
    
"""
    filename = "foo.py"
    test_file = make_test_file(filename, file_contents)
    arguments = [test_file] + test_len
    line_checker.main(arguments)
    captured_output = capsys.readouterr().out
    assert "[FAIL]" in captured_output
    for line in exp_result:
        assert line in captured_output
    print(arguments)


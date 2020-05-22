import pytest

from src import line_checker


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
    result = line_checker.checker(line_data)
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
    result = line_checker.checker(line_data)
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
    result = line_checker.checker(line_data)
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
        "    main()  # this is a call to the main function.  the main function "
        "is where it is all at.  just call main()",
        "",
    ]
    result = line_checker.checker(line_data)
    assert len(result) == 3
    assert result == [(5, 102), (6, 85), (10, 110)]


def test_display_check_completed(capsys):
    line_checker.display_check_completed()
    captured_output = capsys.readouterr().out
    assert "1 file checked" in captured_output


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


def test_argument_parsing_file():
    result = line_checker.argument_parsing(["test.py"])
    assert result.file == "test.py"


def test_argument_parsing_no_arguments():
    with pytest.raises(SystemExit):
        line_checker.argument_parsing([])


def test_argument_parsing_help(capsys):
    with pytest.raises(SystemExit):
        line_checker.argument_parsing(["-h"])
    captured_output = capsys.readouterr().out
    assert "usage" in captured_output

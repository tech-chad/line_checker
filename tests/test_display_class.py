from line_checker import line_checker


def test_display_welcome(capsys):
    test_display = line_checker.Display()
    test_display.welcome()
    captured = capsys.readouterr().out
    assert captured == "Line Checker\n"


def test_summary_zero_checked(capsys):
    test_display = line_checker.Display()
    test_display.summary(0, 0)
    captured = capsys.readouterr().out
    assert captured == "0 files checked\n"


def test_summary_one_check_zero_fails(capsys):
    test_display = line_checker.Display()
    test_display.summary(1, 0)
    captured = capsys.readouterr().out
    assert captured == "1 files checked: passed\n"


def test_summary_one_checked_one_failed(capsys):
    test_display = line_checker.Display()
    test_display.summary(1, 1)
    captured = capsys.readouterr().out
    assert captured == "1 files checked: failed\n"


def test_summary_two_checked_one_failed(capsys):
    test_display = line_checker.Display()
    test_display.summary(2, 1)
    captured = capsys.readouterr().out
    assert captured == "2 files checked: 1 passed, 1 failed\n"


def test_summary_failed_details(capsys):
    filename = "foo.py"
    failed_lines = [(10, 85), (34, 89), (78, 102)]
    test_display = line_checker.Display()
    test_display.failed_details(filename, failed_lines)
    captured = capsys.readouterr().out
    assert f"""{filename}
  line: {failed_lines[0][0] + 1}  -  length: {failed_lines[0][1]}
  line: {failed_lines[1][0] + 1}  -  length: {failed_lines[1][1]}
  line: {failed_lines[2][0] + 1}  -  length: {failed_lines[2][1]}
""" in captured


def test_error(capsys):
    test_display = line_checker.Display()
    test_display.error("Error: file not found")
    captured = capsys.readouterr().out
    assert captured == "Error: file not found\n"


def test_display_full_file_passed(capsys):
    test_display = line_checker.Display()
    test_display.welcome()
    captured = capsys.readouterr().out
    assert captured == "Line Checker\n"
    test_display.summary(1, 0)
    captured = capsys.readouterr().out
    assert captured == "1 files checked: passed\n"


def test_display_full_file_failed(capsys):
    test_display = line_checker.Display()
    test_display.welcome()
    captured = capsys.readouterr().out
    assert captured == "Line Checker\n"
    test_display.summary(1, 1)
    captured = capsys.readouterr().out
    assert captured == "1 files checked: failed\n"
    test_display.failed_details("foo.py", [(33, 85), (84, 91)])
    captured = capsys.readouterr().out
    assert captured == """foo.py
  line: 34  -  length: 85
  line: 85  -  length: 91
"""

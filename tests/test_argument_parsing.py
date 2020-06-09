import pytest

from line_checker import line_checker


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


@pytest.mark.parametrize("test_args, expected_result", [
    (["foo.py"], False), (["foo.py", "-E"], True)
])
def test_argument_parsing_elapse_time(test_args, expected_result):
    result = line_checker.argument_parsing(test_args)
    assert result.elapse_time == expected_result


def test_argument_parsing_no_arguments():
    with pytest.raises(SystemExit):
        line_checker.argument_parsing([])


def test_argument_parsing_help(capsys):
    with pytest.raises(SystemExit):
        line_checker.argument_parsing(["-h"])
    captured_output = capsys.readouterr().out
    assert "usage" in captured_output


@pytest.mark.parametrize("test_args, expected_result", [
    (["foo.py"], True), (["foo.py", "--no_color"], False),
])
def test_argument_parsing_no_color(test_args, expected_result):
    result = line_checker.argument_parsing(test_args)
    assert result.color == expected_result


@pytest.mark.parametrize("test_args, expected_result", [
    (["foo.py"], False), (["foo.py", "-q"], True)
])
def test_argument_parsing_quiet_mode(test_args, expected_result):
    result = line_checker.argument_parsing(test_args)
    assert result.quiet_mode == expected_result


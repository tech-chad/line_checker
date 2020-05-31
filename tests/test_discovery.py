import pytest

from line_checker import line_checker


def test_discovery_single_python_file(make_test_file):
    filename = "foo.py"
    test_file = make_test_file(filename, "")
    result = line_checker.discovery(test_file, ["python"])
    assert result == [test_file]


def test_discovery_single_non_python_file(make_test_file):
    filename = "bar.txt"
    test_file = make_test_file(filename, "")
    result = line_checker.discovery(test_file, ["python"])
    assert result == []


def test_discovery_single_file_not_found(tmpdir):
    td = tmpdir.join("test.py")
    with pytest.raises(ValueError):
        line_checker.discovery(td.strpath, ["python"])


@pytest.mark.parametrize("files, expected_results", [
    (["foo.py", "bar.txt"], ["foo.py"]),
    (["foo.txt", "bar.txt"], []),
    (["foo.py", "bar.py"], ["foo.py", "bar.py"]),

    (["text.yml", "t.py", "README.md", "foo.py", "bar.py"],
     ["foo.py", "t.py", "bar.py"]),
])
def test_discovery_files_in_dir(make_temp_directory, files, expected_results):
    temp_dir = make_temp_directory()
    temp_dir.add_directories_root(["test"])
    for f in files:
        temp_dir.add_empty_file(f)
    td = temp_dir.get_temp_directory()
    result = line_checker.discovery(td, ["python"])
    for x in expected_results:
        assert x in " ".join(result)  # TODO do this assert better
    # assert result == expected_results

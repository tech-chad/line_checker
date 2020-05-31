import os.path
import pytest

from line_checker import line_checker


# @pytest.fixture
# def make_test_directory(tmpdir):
#
#     t = tmpdir.mkdir("test")
#     t.join()
#     # def _make_test_file(filename, file_contents):
#     #     t = tmpdir.join(filename)
#     #     t.write(file_contents)
#     #     return t.strpath
#
#     return _make_test_file
@pytest.fixture
def make_test_file(tmpdir):
    def _make_test_file(filename, file_contents):
        t = tmpdir.join(filename)
        t.write(file_contents)
        return t.strpath

    return _make_test_file


@pytest.fixture
def make_test_directory(tmpdir):
    def _make_test_dir(filename_list):
        temp_dir = tmpdir
        temp_dir.mkdir("test")
        os.chdir(temp_dir)
        for name in filename_list:
            with open(name, "w") as f:
                f.write("")
            # temp_dir.join(name).ensure()
            # temp_dir.write("")
        return temp_dir.strpath
    return _make_test_dir


@pytest.fixture
def make_temp_directory(tmpdir):
    class TempDirectory:
        def __init__(self):
            self.temp_dir = tmpdir
            os.chdir(self.temp_dir)
            self.directory_list = []

        def add_directories_root(self, dir_name_list):
            for name in dir_name_list:
                self.temp_dir.mkdir(name)
                self.directory_list.append(name)

        def add_empty_file(self, filename, dir_name=None):
            if dir_name and dir_name in self.directory_list:
                os.chdir(dir_name)
                with open(filename, "w") as f:
                    f.write(" ")
                os.chdir("..")
            else:
                with open(filename, "w") as f:
                    f.write(" ")

        def get_temp_directory(self, dir_name=None):
            if dir_name and dir_name in self.directory_list:
                os.chdir(dir_name)
            return self.temp_dir.strpath

    return TempDirectory


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






import os
import pytest


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
            self.file_list = []

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
            self.file_list.append(filename)

        def add_file(self, filename, contents):
            with open(filename, "w") as f:
                f.write(contents)
            self.file_list.append(filename)

        def get_temp_directory(self, dir_name=None):
            if dir_name and dir_name in self.directory_list:
                os.chdir(dir_name)
            return self.temp_dir.strpath

    return TempDirectory

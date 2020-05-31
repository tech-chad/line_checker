from unittest import mock

from line_checker import line_checker


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
    result = elapse_time.elapse_time()
    assert result == 2.5

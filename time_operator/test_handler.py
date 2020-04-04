import pytest


def dummy():
    return True


def raise_error():
    raise ValueError()


def test_dummy():
    assert dummy() is True


def test_raise_error():
    with pytest.raises(ValueError):
        raise_error()

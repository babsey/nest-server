from nest_server.helpers import str2bool


def test_str2bool():
    assert not str2bool()

    for value in ("1", "t", "true", "y", "yes"):
        assert str2bool(value)

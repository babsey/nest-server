from nest_server.helpers import clean_code, str2bool


def test_clean_code():
    source = "import nest\nnest.ResetKernel()"
    assert clean_code(source) == "#" + source


def test_str2bool():
    assert not str2bool()

    for value in ("1", "t", "true", "y", "yes"):
        assert str2bool(value)

from nest_server.helpers import clean_code


def test_clean_code():
    source = "import nest\nnest.ResetKernel()"
    assert clean_code(source) == "#" + source

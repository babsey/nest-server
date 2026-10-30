from nest_server.helpers import clean_code


def test_clean_code_no_imports():
    source = "x = 1"
    assert clean_code(source) == source


def test_clean_code_comments_from_imports():
    source = "from nest import Create\nCreate('iaf_psc_alpha')"
    assert clean_code(source) == "#" + source


def test_clean_code_keeps_line_count():
    source = "import nest\nimport numpy as np\n\nx = 1\nfrom os import path\ny = 2"
    cleaned = clean_code(source)
    assert len(cleaned.split("\n")) == len(source.split("\n"))
    assert cleaned.split("\n") == ["#import nest", "#import numpy as np", "", "x = 1", "#from os import path", "y = 2"]


def test_clean_code_ignores_indented_imports():
    source = "if True:\n    import nest"
    assert clean_code(source) == source


def test_clean_code_without_imports():
    source = "x = 1\nprint(x)"
    assert clean_code(source) == source


def test_clean_code_empty_source():
    assert clean_code("") == ""

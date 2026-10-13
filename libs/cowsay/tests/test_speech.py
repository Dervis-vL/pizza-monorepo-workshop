from cowsay import get_output_string


def test_the_cow_says_the_text() -> None:
    out = get_output_string("cow", "one workspace")
    assert "< one workspace >" in out
    assert "pizza-loving cow" in out

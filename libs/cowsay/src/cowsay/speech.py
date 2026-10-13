"""A cow that only talks about pizza. Same call as PyPI's cowsay, a very different cow."""

COW = r"""
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""


def get_output_string(char: str, text: str) -> str:
    """Wrap text in a speech bubble and let the cow say it."""
    line = "-" * (len(text) + 2)
    return f" {line}\n< {text} >\n {line}{COW} ~ a pizza-loving {char}\n"

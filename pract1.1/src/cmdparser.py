"""Parser of command lines with support for quoted arguments."""
import shlex

COMMENT_CHAR = "#"
QUOTES = "'\""
BACKSLASH = "\\"
ERROR_TEXTS = (
    ("quotation", "не закрыта кавычка"),
    ("escaped", "обрыв после символа '\\'"),
)


class ParseError(Exception):
    """Raised when a command line cannot be split into tokens."""


def _describe(error):
    """Translate a shlex error into a message for the user."""
    text = str(error)
    for key, message in ERROR_TEXTS:
        if key in text:
            return message
    return text


def _starts_word(line, index):
    """Tell whether the character at index begins a new word."""
    return index == 0 or line[index - 1].isspace()


def _strip_comment(line):
    """Cut off a comment: an unquoted '#' at the start of a word."""
    quote = ""
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
        elif char == BACKSLASH and quote != "'":
            escaped = True
        elif quote:
            if char == quote:
                quote = ""
        elif char in QUOTES:
            quote = char
        elif char == COMMENT_CHAR and _starts_word(line, index):
            return line[:index]
    return line


def parse_line(line):
    """Split a command line into tokens.

    Single quotes, double quotes and backslash escapes are supported.
    An unquoted '#' at the start of a word begins a comment, as in
    bash. An empty list is returned for blank lines and comments.
    Raises ParseError on broken quoting.
    """
    lexer = shlex.shlex(_strip_comment(line), posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError as error:
        raise ParseError(_describe(error)) from error

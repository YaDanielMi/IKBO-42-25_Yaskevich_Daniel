"""Tests of the command line parser."""
import unittest

from cmdparser import ParseError, parse_line


class ParseLineTest(unittest.TestCase):
    """Splitting of command lines into tokens."""

    def test_plain_words(self):
        self.assertEqual(parse_line("ls -l /tmp"), ["ls", "-l", "/tmp"])

    def test_extra_spaces(self):
        self.assertEqual(parse_line("  cd    dir  "), ["cd", "dir"])

    def test_double_quotes_keep_spaces(self):
        self.assertEqual(
            parse_line('ls "my dir" b'), ["ls", "my dir", "b"]
        )

    def test_single_quotes_keep_spaces(self):
        self.assertEqual(parse_line("cd 'a  b'"), ["cd", "a  b"])

    def test_quotes_inside_a_word(self):
        self.assertEqual(parse_line('ls a"b c"d'), ["ls", "ab cd"])

    def test_empty_quoted_argument(self):
        self.assertEqual(parse_line('ls ""'), ["ls", ""])

    def test_escaped_space(self):
        self.assertEqual(parse_line(r"cd my\ dir"), ["cd", "my dir"])

    def test_blank_line(self):
        self.assertEqual(parse_line("   "), [])

    def test_comment_line(self):
        self.assertEqual(parse_line("# just a comment"), [])

    def test_trailing_comment(self):
        self.assertEqual(parse_line("ls a # note"), ["ls", "a"])

    def test_hash_inside_word_is_text(self):
        self.assertEqual(parse_line("echo a#b c"), ["echo", "a#b", "c"])

    def test_hash_after_quoted_text_is_comment(self):
        self.assertEqual(parse_line("ls 'a b' #x"), ["ls", "a b"])

    def test_escaped_hash_is_text(self):
        self.assertEqual(parse_line(r"ls \#x"), ["ls", "#x"])

    def test_hash_inside_quotes_is_text(self):
        self.assertEqual(parse_line('ls "#1"'), ["ls", "#1"])

    def test_unclosed_double_quote(self):
        with self.assertRaises(ParseError):
            parse_line('ls "oops')

    def test_unclosed_single_quote(self):
        with self.assertRaises(ParseError):
            parse_line("ls 'oops")

    def test_dangling_backslash(self):
        with self.assertRaises(ParseError):
            parse_line("ls abc\\")


if __name__ == "__main__":
    unittest.main()

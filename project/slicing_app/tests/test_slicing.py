import unittest

import rstr
from project.slicing_app import extract_songs_info

valid_line = rstr.xeger(r"\w*\d\d:\d\d:\d\d\w*")
invalid_line = rstr.xeger(r"\w*")
empty_line = " "

multiple_valid_lines = "\n".join([valid_line] * 10)
valid_invalid_lines = "\n".join([valid_line, valid_line, invalid_line])
valid_invalid_empty_lines = "\n".join([valid_line, empty_line, invalid_line])
valid_empty_lines = "\n".join([empty_line, valid_line, empty_line, valid_line])
multiple_invalid_lines = "\n".join([invalid_line, invalid_line, invalid_line])
invalid_empty_lines = "\n".join([invalid_line, empty_line, invalid_line])
multiple_empty_lines = "\n".join([empty_line, empty_line, empty_line])


# TODO: Adjust, legacy code.
class TestExtractSongsInfo(unittest.TestCase):
    """
    Tests if there is at least one valid line in text, in which slicing
    time can be detected.
    """

    def test_invalid_input(self):
        self.assertRaises(ValueError, extract_songs_info, valid_invalid_empty_lines)
        self.assertRaises(ValueError, extract_songs_info, multiple_invalid_lines)
        self.assertRaises(ValueError, extract_songs_info, valid_invalid_lines)
        self.assertRaises(ValueError, extract_songs_info, multiple_empty_lines)
        self.assertRaises(ValueError, extract_songs_info, invalid_empty_lines)
        self.assertRaises(ValueError, extract_songs_info, empty_line)
        self.assertRaises(ValueError, extract_songs_info, invalid_line)
        self.assertRaises(AttributeError, extract_songs_info, 123)
        self.assertRaises(AttributeError, extract_songs_info, True)
        self.assertRaises(AttributeError, extract_songs_info, [])

    def test_valid_input(self):
        self.assertIsInstance(extract_songs_info(valid_line), dict)
        self.assertIsInstance(extract_songs_info(multiple_valid_lines), dict)
        self.assertIsInstance(extract_songs_info(valid_empty_lines), dict)

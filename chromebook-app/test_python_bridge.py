"""Known-answer and boundary cases for the Year 10 Python extension."""

import unittest

from python_bridge import command_for, count_active


class CommandTests(unittest.TestCase):
    def test_every_valid_command(self):
        cases = (
            ("light", "on", "ON"),
            ("light", "off", "OFF"),
            ("garage", "open", "OPEN"),
            ("garage", "close", "CLOSE"),
            ("door", "open", "ON"),
            ("door", "close", "OFF"),
        )
        for device, action, expected in cases:
            with self.subTest(device=device, action=action):
                self.assertEqual(command_for(device, action), expected)

    def test_unknown_command(self):
        self.assertIsNone(command_for("light", "close"))
        self.assertIsNone(command_for("fan", "on"))


class CountTests(unittest.TestCase):
    def test_zero_and_all_active(self):
        self.assertEqual(count_active({"light": False, "garage": False, "door": False}), 0)
        self.assertEqual(count_active({"light": True, "garage": True, "door": True}), 3)

    def test_unknown_is_not_active(self):
        self.assertEqual(count_active({"light": True, "garage": None, "door": False}), 1)


if __name__ == "__main__":
    unittest.main()

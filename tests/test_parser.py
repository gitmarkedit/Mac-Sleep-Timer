"""Юнит-тесты для парсера времени sleep_timer.parser."""

import unittest

from sleep_timer.parser import parse_duration


class TestParser(unittest.TestCase):
    """Тестирование функции parse_duration."""

    def test_default_minutes(self):
        self.assertEqual(parse_duration("30"), 1800)
        self.assertEqual(parse_duration("45"), 2700)
        self.assertEqual(parse_duration("60"), 3600)
        self.assertEqual(parse_duration("1"), 60)

    def test_minute_suffixes(self):
        self.assertEqual(parse_duration("15m"), 900)
        self.assertEqual(parse_duration("30min"), 1800)
        self.assertEqual(parse_duration("45мин"), 2700)
        self.assertEqual(parse_duration("30 минут"), 1800)
        self.assertEqual(parse_duration("1 минута"), 60)

    def test_hour_suffixes(self):
        self.assertEqual(parse_duration("1h"), 3600)
        self.assertEqual(parse_duration("1hr"), 3600)
        self.assertEqual(parse_duration("1ч"), 3600)
        self.assertEqual(parse_duration("1 час"), 3600)
        self.assertEqual(parse_duration("2 часа"), 7200)

    def test_fractional_hours(self):
        self.assertEqual(parse_duration("1.5h"), 5400)
        self.assertEqual(parse_duration("1,5ч"), 5400)
        self.assertEqual(parse_duration("0.5h"), 1800)
        self.assertEqual(parse_duration("0,5 часа"), 1800)
        self.assertEqual(parse_duration("2.5h"), 9000)

    def test_second_suffixes(self):
        self.assertEqual(parse_duration("30s"), 30)
        self.assertEqual(parse_duration("45сек"), 45)
        self.assertEqual(parse_duration("60 sec"), 60)

    def test_colon_format(self):
        self.assertEqual(parse_duration("1:30"), 5400)
        self.assertEqual(parse_duration("0:45"), 2700)
        self.assertEqual(parse_duration("2:00"), 7200)
        self.assertEqual(parse_duration("0:15"), 900)

    def test_compound_formats(self):
        self.assertEqual(parse_duration("1h 30m"), 5400)
        self.assertEqual(parse_duration("1 час 15 мин"), 4500)
        self.assertEqual(parse_duration("2ч 10м"), 7800)

    def test_invalid_inputs(self):
        invalid_cases = ["", "   ", "abc", "-5", "0", "0m", "invalid", "!!", "-1h"]
        for case in invalid_cases:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    parse_duration(case)


if __name__ == "__main__":
    unittest.main()

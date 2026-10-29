import unittest
from collections.abc import Iterable

from shapes.rectangle import Rectangle


class RectangleTests(unittest.TestCase):
    def test_requires_length_and_width(self):
        with self.assertRaises(TypeError):
            Rectangle(5)
        with self.assertRaises(TypeError):
            Rectangle()

    def test_stores_length_and_width(self):
        rect = Rectangle(10, 5)
        self.assertEqual(rect.length, 10)
        self.assertEqual(rect.width, 5)

    def test_rejects_non_int_values(self):
        for bad in ("5", 5.5, None, True):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    Rectangle(bad, 3)
                with self.assertRaises(TypeError):
                    Rectangle(3, bad)

    def test_is_iterable(self):
        self.assertIsInstance(Rectangle(1, 2), Iterable)

    def test_iteration_yields_length_then_width(self):
        self.assertEqual(
            list(Rectangle(10, 5)),
            [{"length": 10}, {"width": 5}],
        )

    def test_for_loop_order(self):
        seen = [item for item in Rectangle(7, 3)]
        self.assertEqual(seen[0], {"length": 7})
        self.assertEqual(seen[1], {"width": 3})
        self.assertEqual(len(seen), 2)

    def test_can_be_iterated_more_than_once(self):
        rect = Rectangle(4, 2)
        self.assertEqual(list(rect), list(rect))


if __name__ == "__main__":
    unittest.main()

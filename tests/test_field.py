import unittest

from src.field import Field


class FieldTest(unittest.TestCase):
    def setUp(self):
        self.field = Field()

    def tearDown(self):
        return super().tearDown()

    def test_init(self):
        self.assertEqual(self.field.height, 6)
        self.assertEqual(self.field.width, 7)
        self.assertEqual(self.field.chain_length, 4)

    def test_overflow(self):
        for row in range(self.field.height):
            self.assertEqual(self.field.make_move(row, 0), 0)
            self.assertEqual(self.field.make_move(row, 1), 0)

        self.assertEqual(self.field.make_move(0, 0), -1)

    def test_lowest_row(self):
        size = 4
        for row in range(size):
            self.field.make_move(0, 0)
        for row in range(self.field.height - size):
            self.assertEqual(self.field.field_storage[row][0], " ")

    def test_win_main_diag(self):
        self.field.make_move(5, 6)
        self.field.make_move(0, 0)
        self.field.make_move(4, 5)
        self.field.make_move(0, 0)
        self.field.make_move(3, 4)
        self.field.make_move(0, 0)
        self.assertFalse(self.field.is_win()[0])
        self.field.make_move(2, 3)
        self.assertTrue(self.field.is_win()[0])

    def test_win_side_diag(self):
        self.field.make_move(3, 3)
        self.field.make_move(0, 0)
        self.field.make_move(2, 4)
        self.field.make_move(0, 0)
        self.field.make_move(1, 5)
        self.field.make_move(0, 0)
        self.assertFalse(self.field.is_win()[0])
        self.field.make_move(0, 6)
        self.assertTrue(self.field.is_win()[0])

    def test_win_horizontal(self):
        self.field.make_move(0, 0)
        self.field.make_move(0, 4)
        self.field.make_move(0, 1)
        self.field.make_move(0, 4)
        self.field.make_move(0, 2)
        self.field.make_move(0, 4)
        self.assertFalse(self.field.is_win()[0])
        self.field.make_move(0, 3)
        self.assertTrue(self.field.is_win()[0])

    def test_win_vertical(self):
        self.field.make_move(3, 3)
        self.field.make_move(1, 1)
        self.field.make_move(0, 0)
        self.field.make_move(1, 1)
        self.field.make_move(0, 0)
        self.field.make_move(1, 1)
        self.field.make_move(0, 0)
        self.assertFalse(self.field.is_win()[0])
        self.field.make_move(1, 1)
        self.assertTrue(self.field.is_win()[0])

    def test_draw(self):
        moves = []
        for i in range(0, 14, 2):
            for j in range(3):
                moves.append(i % 7)
                moves.append((i + 1) % 7)

        for move in moves:
            self.field.make_move(0, move)
        self.assertTrue(self.field.is_game_over(), (True, (-1, -1), ""))

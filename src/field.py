from typing import Union


class Point:
    """
        Represents a point on a 2D grid.

    Attributes:
        x (int): The x-coordinate of the point.
        y (int): The y-coordinate of the point.
    """

    def __init__(self, x: int, y: int) -> None:
        """
            Initializes a new Point object.

        :param x: The x-coordinate of the point.
        :param y: The y-coordinate of the point.
        """
        self.x = x
        self.y = y

    def __add__(self, other: "Point") -> "Point":
        """
            Returns a new Point that is the sum of the given points.

        :param other: The other point to add.
        :return: A new Point that is the sum of the given points.
        """
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        """
            Returns a new Point that is the difference of the given points.

        :param other: The other point to subtract.
        :return: A new Point that is the difference of the given points.
        """
        return Point(self.x - other.x, self.y - other.y)

    def __lt__(self, other: "Point") -> bool:
        """
            Checks if the given point is less than the current point.

        :param other: The point to compare with.
        :return: True if the given point is less than the current point.
        """
        return self.x < other.x and self.y < other.y

    def __eq__(self, other: "Point") -> bool:
        """
            Checks if the given point is equal to the current point.

        :param other: The point to compare with.
        :return: True if the given point is equal to the current point.
        """
        return self.x == other.x and self.y == other.y

    def __mul__(self, coefficient: int) -> "Point":
        """
            Returns a new Point that is the product of the given point and the coefficient.

        :param coefficient: The coefficient to multiply the point with.
        :return: A new Point that is the product of the given point and the coefficient.
        """
        return Point(self.x * coefficient, self.y * coefficient)


def at(point: "Point", arr: list) -> str:
    """
        Returns the value at the given point in the 2D array.

    :param point: The point to get the value from.
    :param arr: The 2D array to get the value from.
    :return: The value at the given point in the 2D array.
    """
    return arr[point.y][point.x]


class Field:
    """
    Represents a game field for a Connect Four-like game.

    Attributes:
        height (int): The height of the game field.
        width (int): The width of the game field.
        chain_length (int): The length of the chain required to win.
        field_storage (list[list[str]]): A 2D list representing the game field.
        full_cells_count (int): The number of cells that have been filled.

    """

    def __init__(self):
        """
        Initializes a new Field object.

        The game field is initialized with default values:
        height = 6
        width = 7
        chain_length = 4

        The game field is represented as a 2D list, and is initially filled with spaces.
        The number of cells that have been filled is set to 0.

        """
        self.height = 6
        self.width = 7
        self.chain_length = 4
        self.field_storage = [[" "] * self.width for i in range(self.height)]
        self.full_cells_count = 0

    def make_move(self, row: int, column: int) -> int:
        """
        Processes a move in the game.

        :param row: The row of the move.
        :param column: The column of the move.
        :return: 0 if the move was successful, -1 if the move was invalid.
        """
        if self.field_storage[0][column] != " ":
            return -1
        symbol = "x"
        if self.full_cells_count % 2 == 1:
            symbol = "o"

        for row in range(self.height - 1, -1, -1):
            if self.field_storage[row][column] == " ":
                self.field_storage[row][column] = symbol
                break
        self.full_cells_count += 1
        return 0

    def is_win(self) -> tuple[bool, int, int, Point]:
        """
            Checks if there is a winning chain on the game field.

        :return: A tuple containing a boolean indicating if there is a win, the row and column of the win, and the direction of the win (Point).
        """
        for dir in [Point(1, 0), Point(0, 1), Point(1, 1)]:
            for row in range(self.height - dir.y * (self.chain_length - 1)):
                for column in range(self.width - dir.x * (self.chain_length - 1)):
                    start = Point(column, row)
                    is_same = at(start, self.field_storage) != " "
                    for k in range(self.chain_length - 1):
                        is_same = is_same and (
                            at(start + dir * k, self.field_storage)
                            == at(start + dir * (k + 1), self.field_storage)
                        )
                    if is_same:
                        return True, row, column, dir

        for row in range(self.chain_length - 1, self.height):
            for column in range(self.width - self.chain_length + 1):
                is_same = self.field_storage[row][column] != " "
                for k in range(self.chain_length - 1):
                    is_same = is_same and (
                        self.field_storage[row - k][column + k]
                        == self.field_storage[row - k - 1][column + k + 1]
                    )
                if is_same:
                    return True, row, column, Point(1, -1)
        return False, 0, 0, Point(0, 0)

    def is_game_over(self) -> tuple[bool, tuple[int, int], Union[str, Point]]:
        """
            Checks if the game is over and its result: WIN, LOSE, or DRAW.

        :return: A tuple containing a boolean indicating if the game is over, the coordinates of the winning chain, and its direction (or an empty string if it is a draw).
        """
        is_win, y, x, dir = self.is_win()
        if is_win:
            return is_win, (y, x), dir
        elif self.width * self.height == self.full_cells_count:
            return True, (-1, -1), ""
        return False, (-1, -1), ""

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __mul__(self, coefficient):
        return Point(self.x * coefficient, self.y * coefficient)


def at(point, arr):
    return arr[point.y][point.x]


class Field:
    def __init__(self):
        self.height = 6
        self.width = 7
        self.chain_length = 4
        self.field_storage = [[" "] * self.width for i in range(self.height)]
        self.full_cells_count = 0

    def make_move(self, row, column):
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

    def is_win(self):
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

    def is_game_over(self):
        is_win, y, x, dir = self.is_win()
        if is_win:
            return is_win, (y, x), dir
        elif self.width * self.height == self.full_cells_count:
            return True, (-1, -1), ""
        return False, (-1, -1), ""

import random
import copy
from enum import Enum


class Direction(Enum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3


class Item:
    def __init__(self, value=0):
        self._value = value
        self._modified = False

    @property
    def value(self):
        return self._value

    @property
    def is_empty(self):
        return self._value == 0

    def __str__(self):
        return '{:5}'.format(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def increase(self):
        self._value *= 2
        self._modified = True

    def can_merge(self, cell):
        return cell.value == self._value and not self._modified and not cell._modified


class Field:
    def __init__(self, size=4, values=None, init_score=0):
        self._size = size
        if values is None:
            self._values = [[Item() for i in range(size)] for j in range(size)]
        else:
            self._values = values
        if values is None:
            self._generate_new_item()
        self._score = init_score

    @property
    def size(self):
        return self._size

    @property
    def score(self):
        return self._score

    def _move_row(self, row):
        modified = False
        for index, item in enumerate(row):
            if item.is_empty:
                continue
            for new_index in range(index - 1, -1, -1):
                if row[new_index].is_empty:
                    modified = True
                    row[new_index] = item
                    row[new_index + 1] = Item()
                elif row[new_index].can_merge(row[new_index + 1]):
                    modified = True
                    row[new_index].increase()
                    self._score += row[new_index].value
                    row[new_index + 1] = Item()
                else:
                    break
        return row, modified

    def _get_free_cells(self):
        result = []
        for row_index, row in enumerate(self._values):
            for column_index, item in enumerate(row):
                if item.is_empty:
                    result.append((row_index, column_index))
        return result

    @property
    def values(self):
        return self._values

    @property
    def is_over(self):
        if len(self._get_free_cells()) != 0:
            return False
        flag = True
        for i in range(self.size - 1):
            for j in range(self.size):
                flag &= self._values[i][j] != self._values[i + 1][j]
                flag &= self._values[j][i] != self._values[j][i + 1]
        return flag

    def print(self):
        for row in self.values:
            print(*row, sep='')

    def _generate_new_item(self):
        free_cells = self._get_free_cells()
        try:
            cell = random.choice(free_cells)
            self._values[cell[0]][cell[1]] = Item(2)
        except IndexError:
            pass

    def _reset_cells(self):
        for row in self._values:
            for cell in row:
                cell._modified = False

    def _move(self, direction):
        modified = False
        is_vertical = direction.value % 2 == 1
        is_reversed = direction.value in (0, 3)
        for row_index in range(len(self._values)):
            if is_vertical:
                crow = [self._values[i][row_index] for i in range(self._size)]
            else:
                crow = [self._values[row_index][i] for i in range(self._size)]

            if is_reversed:
                crow.reverse()
                new_row, new_modified = self._move_row(crow)
                new_row.reverse()
            else:
                new_row, new_modified = self._move_row(crow)

            modified |= new_modified

            for i in range(self._size):
                if is_vertical:
                    self._values[i][row_index] = new_row[i]
                else:
                    self._values[row_index][i] = new_row[i]
        if modified:
            self._generate_new_item()
        self._reset_cells()
        return modified

    def _copy(self):
        return Field(size=self._size, values=copy.deepcopy(self._values),
                     init_score=self._score)

    def get_moved(self, direction):
        new_field = self._copy()
        result = new_field._move(direction)
        return new_field, result

    def equal_in_row_or_clmn(self, row=True):
        result = False
        for row_index in range(len(self._values)):
            if row:
                crow = [self._values[row_index][i] for i in range(self._size)]
            else:
                crow = [self._values[i][row_index] for i in range(self._size)]

            _, new_modified = self._move_row(crow)
            result |= new_modified
        return result

    @property
    def equal_in_row(self):
        return self.equal_in_row_or_clmn(row=True)

    @property
    def equal_in_column(self):
        return self.equal_in_row_or_clmn(row=False)

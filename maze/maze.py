from typing import Tuple

import numpy as np


class Maze(object):
    def __init__(self, grid: np.ndarray, start_coordinate: Tuple[int, int], end_coordinate: Tuple[int, int]):
        self.grid = grid
        self.length, self.width = np.shape(grid)
        self.start_coordinate = start_coordinate
        self.end_coordinate = end_coordinate
        self.moves = zip([0, 1, 0, -1], [1, 0, -1, 0])  # East - South - West - North
        if not (self.check_coordinate(start_coordinate) and self.check_coordinate(end_coordinate)):
            raise ValueError('invalid start/end coordinate')
        pass

    def display(self):
        canvas = np.empty(self.grid.shape, dtype='str')
        canvas[:] = '#'
        canvas[self.grid] = ' '
        canvas[self.start_coordinate] = 'S'
        canvas[self.end_coordinate] = 'E'
        print(canvas)
        pass

    def check_coordinate(self, coordinate: Tuple[int, int]):
        rdx, cdx = coordinate
        return (0 <= cdx < self.width) and (0 <= rdx < self.length) and self.grid[coordinate]

    def explore_neighbours(self, coordinate: Tuple[int, int]):
        if not self.check_coordinate(coordinate):
            return []
        else:
            neighbours_coordinates = [(coordinate[0] + move[0], coordinate[1] + move[1]) for move in self.moves]
            return [coord for coord in neighbours_coordinates if self.check_coordinate(coord)]

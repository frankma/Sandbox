from unittest import TestCase

import numpy as np

from maze.maze import Maze
from maze.solver import MazeSolver


class TestMazeSolver(TestCase):
    def setUp(self) -> None:
        grid = [[False, False, False, False, False],
                [False, True, True, True, False],
                [False, True, False, True, False],
                [False, True, False, False, False],
                [False, True, True, True, False],
                [False, False, False, True, False],
                [False, False, False, False, False]]
        self.maze = Maze(np.array(grid, dtype=bool), (1, 1), (5, 3))
        self.solver = MazeSolver(self.maze)
        pass

    def test_scan_maze(self):
        self.assertIs(self.solver.problem, self.maze)
        self.solver.scan_maze()  # solver is still a stub: it must run without error
        pass

    def test_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            Maze(self.maze.grid, (0, 0), (5, 3))  # start on a wall
        with self.assertRaises(ValueError):
            Maze(self.maze.grid, (1, 1), (10, 12))  # end off the grid
        pass

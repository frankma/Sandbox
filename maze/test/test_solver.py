from unittest import TestCase

import numpy as np

from maze.maze import Maze
from maze.solver import MazeSolver


class TestMazeSolver(TestCase):
    def setUp(self) -> None:
        grid = np.array([[], []])
        self.maze = Maze(grid, (0, 0), (10, 12))
        self.solver = MazeSolver(self.maze)
        pass

    def test_scan_maze(self):
        pass

from unittest import TestCase

import numpy as np

from maze.maze import Maze


class TestMaze(TestCase):
    def setUp(self) -> None:
        simple_maze = [[False, False, False, False, False],
                       [False, True, True, True, False],
                       [False, True, False, True, False],
                       [False, True, False, False, False],
                       [False, True, True, True, False],
                       [False, False, False, True, False],
                       [False, False, False, False, False]]
        self.simple_maze = Maze(np.array(simple_maze, dtype=bool), (1, 1), (5, 3))
        pass

    def test_explore_neighbours(self):
        no_access = self.simple_maze.explore_neighbours((0, 0))
        self.assertTrue(no_access.__len__() == 0)
        two_accesses = self.simple_maze.explore_neighbours((1, 3))
        self.assertTrue(two_accesses.__len__() == 2)
        no_access_2 = self.simple_maze.explore_neighbours((3, 2))
        self.assertTrue(no_access_2.__len__() == 0)
        pass

    def test_display(self):
        self.simple_maze.display()
        pass

    pass

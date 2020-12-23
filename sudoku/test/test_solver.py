import logging
import sys
from unittest import TestCase

from sudoku.solver import SudokuSolver
from sudoku.sudoku import Sudoku

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestSudoKuSolver(TestCase):
    def setUp(self) -> None:
        self.grid_two_by_two = [[1, 2, 3, 4],
                                [4, 3, 2, 1],
                                [0, 0, 0, 0],
                                [0, 0, 0, 0]]
        self.solver_two_by_two = SudokuSolver(Sudoku.create(self.grid_two_by_two))

        grid_1 = [[0, 6, 2, 0, 0, 5, 0, 0, 0],
                  [0, 0, 9, 0, 0, 6, 1, 0, 0],
                  [0, 3, 0, 2, 0, 9, 0, 6, 0],
                  [9, 2, 0, 0, 4, 0, 0, 0, 6],
                  [5, 0, 0, 0, 8, 0, 0, 0, 3],
                  [8, 0, 0, 0, 9, 0, 0, 4, 7],
                  [0, 5, 0, 9, 0, 1, 0, 3, 0],
                  [0, 0, 7, 3, 0, 0, 6, 0, 0],
                  [0, 0, 0, 7, 0, 0, 8, 5, 0]]
        self.sudoku_1 = Sudoku.create(grid_1)
        self.solver_1 = SudokuSolver(self.sudoku_1)

        grid_2 = [[1, 2, 0, 0],
                  [3, 4, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]]
        self.sudoku_2 = Sudoku.create(grid_2)
        self.solver_2 = SudokuSolver(self.sudoku_2)

        grid_3 = [[0, 8, 0, 0, 2, 0, 5, 6, 0],
                  [0, 0, 0, 1, 0, 0, 0, 0, 7],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 5, 0, 0, 9, 0, 4, 0, 8],
                  [0, 0, 7, 8, 0, 0, 0, 0, 3],
                  [0, 9, 0, 0, 1, 0, 0, 5, 0],
                  [2, 0, 4, 0, 0, 0, 8, 0, 0],
                  [0, 6, 0, 0, 8, 5, 0, 0, 0],
                  [0, 0, 0, 2, 0, 0, 1, 0, 0]]
        self.sudoku_3 = Sudoku.create(grid_3)
        self.solver_3 = SudokuSolver(self.sudoku_3)

        grid_4 = [[5, 6, 0, 1, 0, 0, 0, 3, 0],
                  [9, 0, 0, 0, 2, 0, 6, 0, 0],
                  [0, 1, 0, 0, 0, 0, 0, 0, 2],
                  [0, 0, 3, 6, 0, 0, 7, 0, 9],
                  [0, 0, 0, 0, 8, 0, 0, 0, 4],
                  [0, 5, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 3, 0, 0, 0, 0],
                  [0, 0, 0, 0, 4, 0, 0, 0, 0],
                  [0, 2, 7, 0, 6, 0, 0, 1, 3]]
        self.sudoku_4 = Sudoku.create(grid_4)
        self.solver_4 = SudokuSolver(self.sudoku_4)

        grid_5 = [[0, 0, 0, 4, 0, 0, 0, 0, 0],
                  [0, 5, 0, 7, 0, 0, 0, 0, 9],
                  [0, 0, 0, 9, 0, 8, 6, 0, 1],
                  [9, 6, 4, 0, 0, 0, 0, 8, 0],
                  [0, 0, 7, 0, 0, 0, 9, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [3, 1, 0, 0, 0, 2, 0, 0, 0],
                  [0, 0, 0, 8, 0, 0, 0, 0, 7],
                  [2, 0, 0, 0, 0, 0, 1, 0, 3]]
        self.sudoku_5 = Sudoku.create(grid_5)
        self.solver_5 = SudokuSolver(self.sudoku_5)
        pass

    def tearDown(self) -> None:
        pass

    def test_check_coord_remaining(self):
        self.solver_1.auto_fill()
        pass

    def test_performance(self):
        import cProfile
        import pstats
        profiler = cProfile.Profile()
        profiler.enable()

        self.solver_5.solve()

        profiler.disable()
        # stats = pstats.Stats(profiler).sort_stats('tottime')
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats()
        pass

    def test_solve(self):
        self.solver_1.solve()
        self.solver_2.solve()
        self.solver_3.solve()
        self.solver_4.solve()
        self.solver_5.solve()
        self.assertTrue(self.solver_1.sudoku.unfilled_count == 0)
        self.assertTrue(self.solver_2.sudoku.unfilled_count == 0)
        self.assertTrue(self.solver_3.sudoku.unfilled_count == 0)
        self.assertTrue(self.solver_4.sudoku.unfilled_count == 0)
        self.assertTrue(self.solver_5.sudoku.unfilled_count == 0)
        pass

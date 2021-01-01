import logging
import sys
from unittest import TestCase

from sudoku.solver import SudokuSolver, SolverType
from sudoku.sudoku import Sudoku

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestSudoKuSolver(TestCase):
    def setUp(self) -> None:
        grid_no_trial_needed = [[0, 6, 2, 0, 0, 5, 0, 0, 0],
                                [0, 0, 9, 0, 0, 6, 1, 0, 0],
                                [0, 3, 0, 2, 0, 9, 0, 6, 0],
                                [9, 2, 0, 0, 4, 0, 0, 0, 6],
                                [5, 0, 0, 0, 8, 0, 0, 0, 3],
                                [8, 0, 0, 0, 9, 0, 0, 4, 7],
                                [0, 5, 0, 9, 0, 1, 0, 3, 0],
                                [0, 0, 7, 3, 0, 0, 6, 0, 0],
                                [0, 0, 0, 7, 0, 0, 8, 5, 0]]
        self.solver_no_trial_needed = SudokuSolver(Sudoku.create(grid_no_trial_needed))

        grid_two_by_two = [[1, 2, 0, 0],
                           [3, 4, 0, 0],
                           [0, 0, 0, 0],
                           [0, 0, 0, 0]]
        self.solver_two_by_two = SudokuSolver(Sudoku.create(grid_two_by_two))

        grid_three_by_three = [[5, 6, 0, 1, 0, 0, 0, 3, 0],
                               [9, 0, 0, 0, 2, 0, 6, 0, 0],
                               [0, 1, 0, 0, 0, 0, 0, 0, 2],
                               [0, 0, 3, 6, 0, 0, 7, 0, 9],
                               [0, 0, 0, 0, 8, 0, 0, 0, 4],
                               [0, 5, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 3, 0, 0, 0, 0],
                               [0, 0, 0, 0, 4, 0, 0, 0, 0],
                               [0, 2, 7, 0, 6, 0, 0, 1, 3]]
        self.solver_three_by_three = SudokuSolver(Sudoku.create(grid_three_by_three))

        grid_four_by_four = [[0, 11, 0, 0, 0, 14, 8, 5, 0, 1, 0, 0, 0, 6, 0, 15],
                             [1, 15, 0, 0, 3, 2, 0, 0, 0, 13, 0, 16, 8, 0, 0, 10],
                             [4, 14, 9, 0, 0, 13, 10, 12, 0, 5, 8, 15, 0, 3, 2, 11],
                             [0, 12, 0, 8, 7, 15, 9, 0, 3, 0, 2, 11, 1, 14, 0, 0],
                             [0, 0, 11, 15, 0, 0, 0, 0, 0, 0, 14, 0, 5, 4, 0, 1],
                             [0, 0, 0, 0, 12, 3, 15, 14, 10, 2, 0, 1, 9, 8, 0, 0],
                             [7, 8, 12, 0, 0, 0, 0, 1, 15, 6, 0, 4, 14, 0, 13, 3],
                             [3, 0, 13, 0, 10, 0, 0, 9, 8, 7, 0, 0, 0, 0, 6, 16],
                             [15, 2, 10, 13, 5, 16, 0, 0, 0, 0, 7, 0, 3, 11, 0, 8],
                             [8, 3, 16, 11, 9, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0],
                             [0, 4, 0, 12, 0, 0, 0, 0, 0, 11, 0, 10, 0, 16, 14, 0],
                             [0, 0, 0, 1, 2, 10, 0, 0, 0, 0, 0, 8, 4, 0, 0, 12],
                             [16, 0, 0, 4, 14, 0, 0, 0, 0, 0, 1, 0, 6, 15, 0, 0],
                             [0, 0, 0, 0, 0, 9, 0, 0, 0, 16, 5, 0, 13, 0, 7, 14],
                             [0, 7, 2, 0, 6, 1, 13, 0, 9, 8, 15, 0, 11, 10, 16, 4],
                             [0, 10, 1, 9, 0, 0, 16, 0, 0, 3, 0, 13, 0, 0, 0, 2]]
        self.solver_four_by_four = SudokuSolver(Sudoku.create(grid_four_by_four))

        grid_medium = [[0, 8, 0, 0, 2, 0, 5, 6, 0],
                       [0, 0, 0, 1, 0, 0, 0, 0, 7],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 5, 0, 0, 9, 0, 4, 0, 8],
                       [0, 0, 7, 8, 0, 0, 0, 0, 3],
                       [0, 9, 0, 0, 1, 0, 0, 5, 0],
                       [2, 0, 4, 0, 0, 0, 8, 0, 0],
                       [0, 6, 0, 0, 8, 5, 0, 0, 0],
                       [0, 0, 0, 2, 0, 0, 1, 0, 0]]
        self.solver_medium = SudokuSolver(Sudoku.create(grid_medium))

        grid_hard = [[0, 0, 5, 0, 0, 8, 0, 0, 0],
                     [1, 0, 6, 0, 0, 3, 0, 0, 4],
                     [0, 0, 2, 0, 0, 0, 0, 0, 7],
                     [0, 0, 1, 0, 0, 4, 0, 0, 0],
                     [0, 0, 0, 0, 8, 0, 0, 6, 0],
                     [0, 7, 0, 0, 0, 0, 0, 0, 0],
                     [9, 0, 0, 5, 3, 0, 0, 0, 0],
                     [0, 0, 0, 6, 0, 0, 8, 0, 1],
                     [0, 0, 0, 0, 2, 0, 0, 4, 9]]
        self.solver_hard = SudokuSolver(Sudoku.create(grid_hard))

        grid_expert = [[0, 0, 0, 4, 0, 0, 0, 0, 0],
                       [0, 5, 0, 7, 0, 0, 0, 0, 9],
                       [0, 0, 0, 9, 0, 8, 6, 0, 1],
                       [9, 6, 4, 0, 0, 0, 0, 8, 0],
                       [0, 0, 7, 0, 0, 0, 9, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [3, 1, 0, 0, 0, 2, 0, 0, 0],
                       [0, 0, 0, 8, 0, 0, 0, 0, 7],
                       [2, 0, 0, 0, 0, 0, 1, 0, 3]]
        self.solver_expert = SudokuSolver(Sudoku.create(grid_expert))
        pass

    def tearDown(self) -> None:
        pass

    def test_auto_complete(self):
        self.solver_no_trial_needed.auto_reduction()
        self.assertTrue(self.solver_no_trial_needed.solution.is_fulfilled)
        pass

    def test_trial_fill(self):
        import cProfile
        import pstats
        profiler = cProfile.Profile()
        profiler.enable()

        self.solver_expert.solve(solver_type=SolverType.LOGICAL)
        self.assertTrue(self.solver_expert.solution.is_fulfilled)

        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('tottime')
        # stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats()
        pass

    def test_backtrack_fill(self):
        import cProfile
        import pstats
        profiler = cProfile.Profile()
        profiler.enable()

        self.solver_expert.solve(solver_type=SolverType.BACKTRACK)
        self.assertTrue(self.solver_expert.solution.is_fulfilled)

        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('tottime')
        # stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats()
        pass

    def test_solve(self):
        solver_no_trial_needed = self.solver_no_trial_needed.__copy__()
        solver_two_by_two = self.solver_two_by_two.__copy__()
        solver_three_by_three = self.solver_three_by_three.__copy__()
        solver_four_by_four = self.solver_four_by_four.__copy__()
        solver_medium = self.solver_medium.__copy__()
        solver_hard = self.solver_hard.__copy__()
        solver_expert = self.solver_expert.__copy__()

        solver_no_trial_needed.solve(solver_type=SolverType.LOGICAL)
        solver_two_by_two.solve(solver_type=SolverType.LOGICAL)
        solver_three_by_three.solve(solver_type=SolverType.LOGICAL)
        solver_four_by_four.solve(solver_type=SolverType.LOGICAL)
        solver_medium.solve(solver_type=SolverType.LOGICAL)
        solver_hard.solve(solver_type=SolverType.LOGICAL)
        solver_expert.solve(solver_type=SolverType.LOGICAL)

        self.assertTrue(solver_no_trial_needed.solution.is_fulfilled)
        self.assertTrue(solver_two_by_two.solution.is_fulfilled)
        self.assertTrue(solver_three_by_three.solution.is_fulfilled)
        self.assertTrue(solver_four_by_four.solution.is_fulfilled)
        self.assertTrue(solver_medium.solution.is_fulfilled)
        self.assertTrue(solver_hard.solution.is_fulfilled)
        self.assertTrue(solver_expert.solution.is_fulfilled)
        solver_no_trial_needed = self.solver_no_trial_needed.__copy__()
        solver_two_by_two = self.solver_two_by_two.__copy__()
        solver_three_by_three = self.solver_three_by_three.__copy__()
        solver_four_by_four = self.solver_four_by_four.__copy__()
        solver_medium = self.solver_medium.__copy__()
        solver_hard = self.solver_hard.__copy__()
        solver_expert = self.solver_expert.__copy__()

        solver_no_trial_needed.solve(solver_type=SolverType.BACKTRACK)
        solver_two_by_two.solve(solver_type=SolverType.BACKTRACK)
        solver_three_by_three.solve(solver_type=SolverType.BACKTRACK)
        solver_four_by_four.solve(solver_type=SolverType.BACKTRACK)
        solver_medium.solve(solver_type=SolverType.BACKTRACK)
        solver_hard.solve(solver_type=SolverType.BACKTRACK)
        solver_expert.solve(solver_type=SolverType.BACKTRACK)

        self.assertTrue(solver_no_trial_needed.solution.is_fulfilled)
        self.assertTrue(solver_two_by_two.solution.is_fulfilled)
        self.assertTrue(solver_three_by_three.solution.is_fulfilled)
        self.assertTrue(solver_four_by_four.solution.is_fulfilled)
        self.assertTrue(solver_medium.solution.is_fulfilled)
        self.assertTrue(solver_hard.solution.is_fulfilled)
        self.assertTrue(solver_expert.solution.is_fulfilled)
        pass

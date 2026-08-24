import logging
import sys
from unittest import TestCase

from sudoku.generator import DIFFICULTY_GIVENS, generate, generate_solved
from sudoku.solver import SolverType, SudokuSolver

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestGenerator(TestCase):
    def test_generate_solved(self):
        solved = generate_solved(rank=3)
        self.assertTrue(solved.is_fulfilled)
        pass

    def test_generate_has_unique_solution(self):
        puzzle = generate(rank=3, difficulty='medium', seed=42)
        givens = puzzle.size ** 2 - puzzle.unfilled_count
        self.assertAlmostEqual(givens, DIFFICULTY_GIVENS['medium'], delta=2)

        solver_a = SudokuSolver(puzzle.__copy__())
        solver_a.solve(solver_type=SolverType.LOGICAL)
        self.assertTrue(solver_a.solution.is_fulfilled)

        solver_b = SudokuSolver(puzzle.__copy__())
        solver_b.solve(solver_type=SolverType.BACKTRACK)
        self.assertTrue(solver_b.solution.is_fulfilled)

        self.assertTrue((solver_a.solution.grid == solver_b.solution.grid).all())
        pass

    def test_generate_difficulties(self):
        for difficulty in DIFFICULTY_GIVENS:
            puzzle = generate(rank=3, difficulty=difficulty, seed=1)
            self.assertTrue(puzzle.unfilled_count > 0)
        pass

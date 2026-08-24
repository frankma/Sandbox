import logging
import random
from typing import Optional

import numpy as np

from sudoku.solver import SudokuSolver
from sudoku.sudoku import Sudoku

logger = logging.getLogger(__name__)

DIFFICULTY_GIVENS = {
    'easy': 40,
    'medium': 32,
    'hard': 28,
    'expert': 24,
}


def generate_solved(rank: int = 3) -> Sudoku:
    size = rank ** 2
    sudoku = Sudoku.create(np.zeros((size, size), dtype=int))
    _fill_randomly(sudoku)
    return sudoku


def generate(rank: int = 3, difficulty: str = 'medium', seed: Optional[int] = None) -> Sudoku:
    if seed is not None:
        random.seed(seed)
    puzzle = generate_solved(rank).__copy__()
    size = rank ** 2
    target_givens = min(DIFFICULTY_GIVENS.get(difficulty, 32), size * size)

    coords = list(puzzle.coord_dim.keys())
    random.shuffle(coords)
    givens = size * size
    for coord in coords:
        if givens <= target_givens:
            break
        backup = puzzle.grid[coord]
        puzzle.grid[coord] = 0
        puzzle.unfilled_count += 1
        if _count_solutions(puzzle, limit=2) == 1:
            givens -= 1
        else:
            puzzle.grid[coord] = backup
            puzzle.unfilled_count -= 1
    return puzzle


def _fill_randomly(sudoku: Sudoku) -> bool:
    coord = next((c for c in sudoku.coord_dim if sudoku.grid[c] == 0), None)
    if coord is None:
        return True
    candidates = list(sudoku.scan_candidates(coord))
    random.shuffle(candidates)
    for value in candidates:
        if sudoku.fill_coord(coord, value):
            if _fill_randomly(sudoku):
                return True
            sudoku.grid[coord] = 0
            sudoku.unfilled_count += 1
    return False


def _count_solutions(sudoku: Sudoku, limit: int = 2) -> int:
    solver = SudokuSolver(sudoku.__copy__())
    counter = {'n': 0}
    _count_rec(solver, limit, counter)
    return counter['n']


def _count_rec(solver: SudokuSolver, limit: int, counter: dict) -> None:
    if counter['n'] >= limit:
        return
    solver.auto_reduction()
    if solver.solution.unfilled_count > solver.coord_candidates.__len__():
        return
    if solver.solution.is_fulfilled:
        counter['n'] += 1
        return
    if not solver.coord_candidates:
        return
    coord = min(solver.coord_candidates, key=(lambda x: solver.coord_candidates[x].__len__()))
    candidates = solver.coord_candidates.pop(coord)
    for value in candidates:
        if counter['n'] >= limit:
            return
        branch = solver.__copy__()
        if branch.fill_coordinates({coord: value}):
            _count_rec(branch, limit, counter)

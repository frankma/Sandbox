import copy
import logging
import time
from enum import Enum
from typing import Dict, Iterator, Optional, Tuple, Set

from sudoku.sudoku import Sudoku

logger = logging.getLogger(__name__)


class SolverType(Enum):
    LOGICAL = 1
    BACKTRACK = 2


class SudokuSolver(object):
    def __init__(self, problem: Sudoku, coordinate_candidates: Dict[Tuple[int, int], Set[int]] = None):
        self.problem = problem.__copy__()  # type: Sudoku
        self.solution = problem.__copy__()  # type: Sudoku
        cc = coordinate_candidates if coordinate_candidates is not None \
            else {c: self.solution.scan_candidates(c) for c in self.solution.coord_dim.keys()}
        self.coord_candidates = {c: cds for c, cds in cc.items() if bool(cds)}  # type:Dict[Tuple[int, int], Set[int]]
        pass

    def __copy__(self) -> 'SudokuSolver':
        return SudokuSolver(self.solution.__copy__(), copy.deepcopy(self.coord_candidates))

    def solve(self, solver_type: SolverType = SolverType.LOGICAL):
        tic = time.perf_counter()

        if solver_type is SolverType.LOGICAL:
            self.solution = self.trial_fill()
        elif solver_type is SolverType.BACKTRACK:
            self.backtrack_fill()
        else:
            raise NotImplemented

        is_solved = self.solution.is_fulfilled
        if is_solved:
            self.coord_candidates.clear()
        logger.info('used %.4f secs through %s method %s sudoku' %
                    (time.perf_counter() - tic, solver_type, 'solved' if is_solved else 'cannot solve'))
        pass

    def fill_coordinates(self, coord_values: Dict[Tuple[int, int], int]) -> bool:
        all_filled = True
        coord_to_refresh = {c: set() for c in self.solution.coord_dim.keys()}
        for coord, value in coord_values.items():
            all_filled &= self.solution.fill_coord(coord, value)
            for c in self.solution.get_relevant_coordinates(coord):
                coord_to_refresh[c].add(value)
        # coord_to_refresh = {c: vs for c, vs in coord_to_refresh.items() if bool(vs)}
        for coord in (coord_to_refresh.keys() & self.coord_candidates.keys()):
            self.coord_candidates[coord] = self.coord_candidates[coord] - coord_to_refresh[coord]
        self.coord_candidates = {c: vs for c, vs in self.coord_candidates.items() if bool(vs)}
        return all_filled

    def auto_reduction(self):
        coord_w_def_val = {c: vs.pop() for c, vs in self.coord_candidates.items() if vs.__len__() == 1}
        while coord_w_def_val.__len__() > 0:
            self.fill_coordinates(coord_w_def_val)
            coord_w_def_val = {c: vs.pop() for c, vs in self.coord_candidates.items() if vs.__len__() == 1}
        pass

    def trial_fill(self) -> Sudoku:
        self.auto_reduction()  # eliminate unnecessary trialing
        if self.solution.is_fulfilled:
            return self.solution
        else:
            # coord, candidates = self.coord_candidates.popitem()
            coord = min(self.coord_candidates, key=(lambda x: self.coord_candidates[x].__len__()))
            candidates = self.coord_candidates.pop(coord)
            for value in candidates:
                solver = self.__copy__()  # branch out the sudoku for trailing
                solver.fill_coordinates({coord: value})
                solver.auto_reduction()
                if solver.solution.unfilled_count > solver.coord_candidates.__len__():
                    continue  # case of insolvable state
                if solver.solution.is_fulfilled:
                    return solver.solution  # case of solution found
                else:
                    solution = solver.trial_fill()
                    if solution is not None:
                        return solution
        pass

    def check_value_possible(self, coord: Tuple[int, int], value: int):
        for sdk_vec, n in self.problem.coord_dim[coord].items():
            if value in self.problem.get_vec(n, sdk_vec):
                return False
        return True

    def backtrack_fill(self):
        unfilled_coordinates = [coord for coord in self.problem.coord_dim.keys() if self.problem.grid[coord] == 0]
        for coord in unfilled_coordinates:
            for value in self.problem.value_set:
                if self.check_value_possible(coord, value):
                    self.problem.grid[coord] = value
                    self.backtrack_fill()
                    self.problem.grid[coord] = 0  # backtracking
            return
        self.solution = self.problem.__copy__()
        pass

    def auto_reduction_steps(self) -> Iterator[Tuple[Tuple[int, int], int, str]]:
        """Generator twin of auto_reduction(); yields (coord, value, 'single') for every forced fill
        as it happens, instead of only returning once fully reduced."""
        coord_w_def_val = {c: vs.pop() for c, vs in self.coord_candidates.items() if vs.__len__() == 1}
        while coord_w_def_val.__len__() > 0:
            for coord, value in coord_w_def_val.items():
                yield coord, value, 'single'
            self.fill_coordinates(coord_w_def_val)
            coord_w_def_val = {c: vs.pop() for c, vs in self.coord_candidates.items() if vs.__len__() == 1}
        pass

    def trial_fill_steps(self) -> Iterator[Tuple[Tuple[int, int], int, str]]:
        """Generator twin of trial_fill(); yields (coord, value, technique) in solving order, where
        technique is 'single' for forced logical fills and 'trial' for guessed cells. Only the
        steps of the successful branch are yielded, mirroring which state trial_fill() would keep.
        Returns True (via StopIteration.value, retrievable with `yield from`) if self.solution
        ends up fulfilled."""
        yield from self.auto_reduction_steps()
        if self.solution.is_fulfilled:
            return True
        coord = min(self.coord_candidates, key=(lambda x: self.coord_candidates[x].__len__()))
        candidates = self.coord_candidates.pop(coord)
        for value in candidates:
            solver = self.__copy__()  # branch out the sudoku for trailing
            solver.fill_coordinates({coord: value})
            branch_steps = list(solver.auto_reduction_steps())
            if solver.solution.unfilled_count > solver.coord_candidates.__len__():
                continue  # case of insolvable state
            if solver.solution.is_fulfilled:
                resolved, tail_steps = True, []
            else:
                sub_gen = solver.trial_fill_steps()
                tail_steps = []
                resolved = False
                try:
                    while True:
                        tail_steps.append(next(sub_gen))
                except StopIteration as si:
                    resolved = bool(si.value)
            if resolved:
                yield coord, value, 'trial'
                for step in branch_steps:
                    yield step
                for step in tail_steps:
                    yield step
                self.solution = solver.solution
                self.coord_candidates = solver.coord_candidates
                return True
        return False

    def solve_steps(self) -> Iterator[Tuple[Tuple[int, int], int, str]]:
        """Generator twin of solve(SolverType.LOGICAL); yields (coord, value, technique) for each
        cell as it is filled, and leaves self.solution/self.coord_candidates in the same end state
        solve() would, once the generator is exhausted."""
        tic = time.perf_counter()
        solved = yield from self.trial_fill_steps()
        if solved:
            self.coord_candidates.clear()
        logger.info('used %.4f secs through step-by-step method %s sudoku' %
                    (time.perf_counter() - tic, 'solved' if solved else 'cannot solve'))
        return solved

    def hint(self) -> Optional[Tuple[Tuple[int, int], int, str]]:
        """Return a single (coord, value, technique) suggestion for the next move without mutating
        this solver's state, or None if already solved/unsolvable. technique is 'single' when the
        value follows directly from row/column/block elimination, or 'trial' when it required
        deeper reasoning to find (deduced by solving the full board)."""
        if self.solution.is_fulfilled:
            return None
        for coord, candidates in self.coord_candidates.items():
            if candidates.__len__() == 1:
                return coord, next(iter(candidates)), 'single'
        solver = self.__copy__()
        solver.solve(SolverType.LOGICAL)
        if not solver.solution.is_fulfilled:
            return None
        coord = min(self.coord_candidates, key=(lambda x: self.coord_candidates[x].__len__()))
        value = int(solver.solution.grid[coord])
        return coord, value, 'trial'

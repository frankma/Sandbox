import copy
import logging
import time
from typing import Dict, Tuple, Set

from sudoku.sudoku import Sudoku

logger = logging.getLogger(__name__)


class SudokuSolver(object):
    def __init__(self, problem: Sudoku, coordinate_candidates: Dict[Tuple[int, int], Set[int]] = None):
        self.sudoku = problem  # type: Sudoku
        cc = coordinate_candidates if coordinate_candidates is not None \
            else {c: self.sudoku.scan_candidates(c) for c in self.sudoku.coord_dim.keys()}
        self.coord_candidates = {c: cds for c, cds in cc.items() if bool(cds)}  # type:Dict[Tuple[int, int], Set[int]]
        pass

    def __copy__(self) -> 'SudokuSolver':
        return SudokuSolver(self.sudoku.__copy__(), copy.deepcopy(self.coord_candidates))

    def solve(self):
        tic = time.perf_counter()
        solution = self.trial_fill()
        if solution is None:
            logger.info('cannot solve sudoku, used %.4f secs' % (time.perf_counter() - tic))
        else:
            self.sudoku = solution
            self.coord_candidates.clear()
            logger.info('solved sudoku in %.4f secs' % (time.perf_counter() - tic))
        pass

    def get_coordinates_with_definite_fill(self) -> Dict[Tuple[int, int], int]:
        coord_w_def_val = [coord for coord, candidates in self.coord_candidates.items() if candidates.__len__() == 1]
        coord_values = {coord: self.coord_candidates.pop(coord).pop() for coord in coord_w_def_val}
        return coord_values

    def fill_coordinates(self, coord_values: Dict[Tuple[int, int], int]) -> bool:
        all_filled = True
        coord_to_refresh = {c: set() for c in self.sudoku.coord_dim.keys()}
        for coord, value in coord_values.items():
            all_filled &= self.sudoku.fill_coord(coord, value)
            for c in self.sudoku.get_relevant_coordinates(coord):
                coord_to_refresh[c].add(value)
        coord_to_refresh = {c: vs for c, vs in coord_to_refresh.items() if bool(vs)}
        for coord in (coord_to_refresh.keys() & self.coord_candidates.keys()):
            self.coord_candidates[coord] = self.coord_candidates[coord] - coord_to_refresh[coord]
        self.coord_candidates = {c: vs for c, vs in self.coord_candidates.items() if bool(vs)}
        return all_filled

    def auto_fill(self):
        coord_to_fill = self.get_coordinates_with_definite_fill()
        while coord_to_fill.__len__() > 0:
            self.fill_coordinates(coord_to_fill)
            coord_to_fill = self.get_coordinates_with_definite_fill()
        pass

    def trial_fill(self) -> Sudoku:
        self.auto_fill()  # eliminate unnecessary trailing
        if self.sudoku.unfilled_count == 0 and self.sudoku.validate_coord(self.sudoku.key_coord):
            return self.sudoku
        else:
            coord, candidates = self.coord_candidates.popitem()
            # coord = min(self.coord_candidates, key=(lambda x: self.coord_candidates[x].__len__()))
            # candidates = self.coord_candidates.pop(coord)
            for value in candidates:
                solver = self.__copy__()  # branch out the sudoku for trailing
                solver.fill_coordinates({coord: value})
                solver.auto_fill()
                if solver.sudoku.unfilled_count > solver.coord_candidates.__len__():
                    continue  # case of insolvable state
                if solver.sudoku.unfilled_count == 0 and solver.sudoku.validate_coord(solver.sudoku.key_coord):
                    return solver.sudoku  # case of solution found
                else:
                    solution = solver.trial_fill()
                    if solution is not None:
                        return solution
        pass

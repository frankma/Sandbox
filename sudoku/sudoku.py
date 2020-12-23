import logging
from enum import Enum
from typing import Dict, Tuple, List, Set

import numpy as np

logger = logging.getLogger(__name__)


class SdkVec(Enum):
    Row = 1
    Column = 2
    Block = 3


class Sudoku(object):
    @classmethod
    def create(cls, grid) -> 'Sudoku':
        gd = np.copy(grid)
        rank = int(np.sqrt(np.sqrt(gd.size)))
        coord_dim, dim_coord = Sudoku.gen_coord_dim_lookups(rank)
        sdk = cls(gd, rank, coord_dim, dim_coord)
        # consistency check
        if any(v < 0 or v > sdk.size for v in np.nditer(sdk.grid)):
            raise ValueError('invalid sudoku value detected')
        if np.shape(grid) != (sdk.size, sdk.size):
            raise ValueError('invalid sudoku for its not squared')
        if not sdk.validate_coord(sdk.key_coord):
            raise ValueError('invalid sudoku grid detected')
        return sdk

    def __init__(self, grid: np.ndarray, rank: int, coord_dim: Dict[Tuple[int, int], Dict[SdkVec, int]],
                 dim_coord: Dict[int, Dict[SdkVec, List[Tuple[int, int]]]]):
        self.grid = grid  # type: np.ndarray
        self.rank = rank  # type: int
        self.size = rank ** 2  # type: int
        self.value_set = frozenset(range(1, self.size + 1))  # type: frozenset
        self.coord_dim = coord_dim  # type: Dict[Tuple[int, int], Dict[SdkVec, int]]
        self.dim_coord = dim_coord  # type: Dict[int, Dict[SdkVec, List[Tuple[int, int]]]]
        self.unfilled_count = np.size(self.grid[self.grid == 0])  # type: int
        self.key_coord = Sudoku.gen_key_coord(self.rank)  # type: List[Tuple[int, int]]
        pass

    def __copy__(self) -> 'Sudoku':
        return Sudoku(np.copy(self.grid), self.rank, self.coord_dim, self.dim_coord)

    def get_vec(self, n: int, sdk_vec: SdkVec) -> np.ndarray:
        return np.array([self.grid[coord] for coord in self.dim_coord[n][sdk_vec]])

    def get_relevant_coordinates(self, coord: Tuple[int, int], skip_filled: bool = True,
                                 skip_self: bool = True) -> Set[Tuple[int, int]]:
        return set(c for sdk_vec, n in self.coord_dim[coord].items() for c in self.dim_coord[n][sdk_vec]
                   if not ((skip_filled and self.grid[c] != 0) or (skip_self and c == coord)))

    def validate_coord(self, coordinates: List[Tuple[int, int]]) -> bool:
        cds = self.coord_dim.keys() & coordinates
        if cds.__len__() is not coordinates.__len__():
            logger.info('requested coordinates out of the grid range, only check for valid coordinates')
        is_valid = cds.__len__() > 0  # case of no coordinate to check, simply fail check
        check_dims = [(n, sdk_vec) for cd in cds for sdk_vec, n in self.coord_dim[cd].items()]
        for n, sdk_vec in check_dims:
            if is_valid:
                is_valid &= Sudoku.check_vec_unique(self.get_vec(n, sdk_vec))
            else:
                break  # exit immediate if invalid point found
        return is_valid

    def fill_coord(self, coordinate: Tuple[int, int], value: int) -> bool:
        is_filled = False
        if coordinate in self.coord_dim and value in self.value_set:
            value_org = self.grid[coordinate]  # make a copy in case of rollback
            self.grid[coordinate] = value
            if self.validate_coord([coordinate]):
                self.unfilled_count -= 1
                is_filled = True
            else:
                self.grid[coordinate] = value_org  # rollback for invalid fill
        return is_filled

    def scan_candidates(self, coordinate: Tuple[int, int]) -> Set[int]:
        candidates = set()
        if self.grid[coordinate] == 0:
            tri_vec = [self.get_vec(n, s) for s, n in self.coord_dim[coordinate].items()]
            candidates = set(self.value_set - set(np.concatenate(tri_vec)))
        return candidates

    @staticmethod
    def check_vec_unique(vec: np.ndarray) -> bool:
        filled_vec = vec[np.nonzero(vec)]
        return np.size(filled_vec) == np.size(np.unique(filled_vec))

    @staticmethod
    def gen_coord_dim_lookups(rank: int):
        size = rank ** 2
        coordinates = [(rdx, cdx) for rdx in range(size) for cdx in range(size)]
        coord_dim = dict()
        dim_coord = dict([(_, {SdkVec.Row: [], SdkVec.Column: [], SdkVec.Block: []}) for _ in range(size)])
        for rdx, cdx in coordinates:
            blc = int(rdx / rank) * rank + int(cdx / rank)
            coord_dim[(rdx, cdx)] = {SdkVec.Row: rdx,
                                     SdkVec.Column: cdx,
                                     SdkVec.Block: blc}
            dim_coord[rdx][SdkVec.Row].append((rdx, cdx))
            dim_coord[cdx][SdkVec.Column].append((rdx, cdx))
            dim_coord[blc][SdkVec.Block].append((rdx, cdx))
        return coord_dim, dim_coord

    @staticmethod
    def gen_key_coord(rank: int) -> List[Tuple[int, int]]:
        size = rank ** 2
        return [(rdx, int(rdx / rank) + (rdx % rank) * rank) for rdx in range(size)]

import logging
import sys
from unittest import TestCase

import numpy as np

from sudoku.sudoku import Sudoku, SdkVec

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestSudoku(TestCase):
    def setUp(self) -> None:
        self.grid_zeros = [[0 for _ in range(9)] for _ in range(9)]
        self.grid_two_by_two = [[1, 3, 2, 4],
                                [2, 4, 1, 3],
                                [3, 0, 0, 0],
                                [4, 0, 0, 0]]
        self.grid_wrong_shape = [[0 for _ in range(8)] for _ in range(2)]
        self.grid_wrong_element = [[1, 3, 1, 0],
                                   [2, 4, 1, 3],
                                   [0, 0, 0, 0],
                                   [0, 0, 0, 0]]
        self.grid_three_by_three = [[0, 0, 0, 4, 0, 0, 0, 0, 0],
                                    [0, 5, 0, 7, 0, 0, 0, 0, 9],
                                    [0, 0, 0, 9, 0, 8, 6, 0, 1],
                                    [9, 6, 4, 0, 0, 0, 0, 8, 0],
                                    [0, 0, 7, 0, 0, 0, 9, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    [3, 1, 0, 0, 0, 2, 0, 0, 0],
                                    [0, 0, 0, 8, 0, 0, 0, 0, 7],
                                    [2, 0, 0, 0, 0, 0, 1, 0, 3]]
        pass

    def tearDown(self) -> None:
        pass

    def test_create(self):
        sudoku_1 = Sudoku.create(self.grid_zeros)
        self.assertTrue(np.all(sudoku_1.grid == 0))

        sudoku_2 = Sudoku.create(self.grid_two_by_two)
        self.assertTrue(np.all((sudoku_2.grid - self.grid_two_by_two) == 0))

        self.assertRaises(ValueError, Sudoku.create, self.grid_wrong_shape)

        self.assertRaises(ValueError, Sudoku.create, self.grid_wrong_element)
        pass

    def test_get_vec(self):
        sudoku = Sudoku.create(self.grid_two_by_two)
        block_indices = [[(0, 0), (0, 1), (1, 0), (1, 1)],
                         [(0, 2), (0, 3), (1, 2), (1, 3)],
                         [(2, 0), (2, 1), (3, 0), (3, 1)],
                         [(2, 2), (2, 3), (3, 2), (3, 3)]]
        for n in range(sudoku.size):
            vec_row = sudoku.get_vec(n, SdkVec.Row)
            grd_row = np.array(self.grid_two_by_two[n])
            self.assertTrue(np.all((grd_row - vec_row) == 0))
            vec_col = sudoku.get_vec(n, SdkVec.Column)
            grd_col = np.array([self.grid_two_by_two[rdx][n] for rdx in range(4)])
            self.assertTrue(np.all((grd_col - vec_col == 0)))
            vec_blc = sudoku.get_vec(n, SdkVec.Block)
            grid_blc = np.array([self.grid_two_by_two[rdx][cdx] for rdx, cdx in block_indices[n]])
            self.assertTrue(np.all((grid_blc - vec_blc) == 0))
        pass

    def test_get_get_relevant_coordinates(self):
        sudoku = Sudoku.create(self.grid_two_by_two)
        coordinates_0_0 = sudoku.get_relevant_coordinates((0, 0))
        self.assertTrue(coordinates_0_0.__len__() == 0)
        coordinates_2_1 = sudoku.get_relevant_coordinates((2, 1))
        self.assertTrue(coordinates_2_1.__len__() == 3)
        coordinates_2_1_sf = sudoku.get_relevant_coordinates((2, 1), skip_filled=False, skip_self=True)
        self.assertTrue(coordinates_2_1_sf.__len__() == 7)
        coordinates_2_1_ss = sudoku.get_relevant_coordinates((2, 1), skip_filled=True, skip_self=False)
        self.assertTrue(coordinates_2_1_ss.__len__() == 4)
        coordinates_2_1_sf_ss = sudoku.get_relevant_coordinates((2, 1), skip_filled=False, skip_self=False)
        self.assertTrue(coordinates_2_1_sf_ss.__len__() == 8)
        pass

    def test_validate_coord(self):
        sudoku = Sudoku.create(self.grid_two_by_two)
        self.assertTrue(sudoku.validate_coord([(rdx, cdx) for rdx in range(4) for cdx in range(4)]))
        sudoku.grid[(0, 0)] = 2  # duplicated value
        self.assertFalse(sudoku.validate_coord([(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (2, 0), (3, 0), (1, 1)]))
        self.assertTrue(sudoku.validate_coord([(1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]))
        pass

    def test_fill_coord(self):
        sudoku = Sudoku.create(self.grid_two_by_two)
        self.assertFalse(sudoku.fill_coord((0, 0), 12))  # invalid value
        self.assertFalse(sudoku.fill_coord((12, 12), 0))  # invalid coordinate
        self.assertFalse(sudoku.fill_coord((0, 0), 3))  # violate consistency rule

        self.assertTrue(sudoku.grid[(3, 3)] == 0)
        self.assertTrue(sudoku.fill_coord((3, 3), 2))
        self.assertTrue(sudoku.grid[(3, 3)] == 2)
        pass

    def test_check_values(self):
        values_all_zeros = np.zeros(9, dtype=int)
        values_one_to_nine = np.array(range(1, 10))
        values_duplicated_one = np.array([0, 1, 1, 0])
        self.assertTrue(Sudoku.check_vec_unique(values_all_zeros))
        self.assertTrue(Sudoku.check_vec_unique(values_one_to_nine))
        self.assertFalse(Sudoku.check_vec_unique(values_duplicated_one))
        pass

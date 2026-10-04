import math
from unittest import TestCase

from heat_equation_finite_difference.solver import (
    TABLE_STEPS, convergence_table, crank_nicolson, exact_solution, initial_condition,
    solve_tridiagonal, value_at)


class TestHeatEquationSolver(TestCase):
    def test_tridiagonal_solver_matches_known_system(self):
        # [2 -1 0; -1 2 -1; 0 -1 2] x = [1 0 1]  ->  x = [1 1 1]
        x = solve_tridiagonal([0, -1, -1], [2, 2, 2], [-1, -1, 0], [1, 0, 1])
        for xi in x:
            self.assertAlmostEqual(xi, 1.0, places=12)

    def test_exact_solution_reproduces_initial_condition(self):
        for x in (0.1, 0.25, 0.5, 0.9):
            self.assertAlmostEqual(exact_solution(x, 0.0, n_terms=2000), initial_condition(x), places=7)

    def test_boundaries_stay_zero(self):
        _, v, _ = crank_nicolson(0.05, 0.0625)
        self.assertEqual(v[0], 0.0)
        self.assertEqual(v[-1], 0.0)

    def test_solution_is_symmetric_about_midpoint(self):
        _, v, _ = crank_nicolson(0.025, 0.03125)
        for i in range(len(v)):
            self.assertAlmostEqual(v[i], v[-1 - i], places=12)

    def test_matches_exact_solution(self):
        exact, rows = convergence_table()
        self.assertLess(abs(rows[-1][3]), 1e-5)

    def test_second_order_convergence(self):
        # Halving both dx and dt should cut the error by about 4.
        _, rows = convergence_table()
        for (_, _, _, e_coarse), (_, _, _, e_fine) in zip(rows, rows[1:]):
            self.assertAlmostEqual(e_coarse / e_fine, 4.0, delta=0.1)

    def test_solution_decays_monotonically(self):
        # Maximum principle: the peak can only shrink with diffusion.
        xs, _, snaps = crank_nicolson(0.05, 0.0625, store_every=1)
        peaks = [value_at(xs, v, 0.5) for _, v in snaps]
        for a, b in zip(peaks, peaks[1:]):
            self.assertLess(b, a)

    def test_table_steps_put_midpoint_on_grid(self):
        for dx, _ in TABLE_STEPS:
            xs, v, _ = crank_nicolson(dx, 0.5)
            self.assertTrue(math.isfinite(value_at(xs, v, 0.5)))

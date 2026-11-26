"""Crank-Nicolson solver for the heat equation with a time-dependent diffusivity.

    V_t = a(t) V_xx,  0 < x < 1,  a(t) = 0.16 + 0.08 sin(t)
    V(x, 0) = x - x^2,  V(0, t) = V(1, t) = 0

Space: 2nd-order centred differences. Time: trapezoid rule (Crank-Nicolson).
Pure Python, no dependencies; run `python3 solver.py` to print the results table.
"""
import math


def diffusivity(t):
    return 0.16 + 0.08 * math.sin(t)


def integrated_diffusivity(t):
    """A(t) = integral of a(s) ds from 0 to t."""
    return 0.16 * t + 0.08 * (1.0 - math.cos(t))


def initial_condition(x):
    return x - x * x


def exact_solution(x, t, n_terms=200):
    """Fourier series solution V = sum_k b_k sin(k pi x) exp(-k^2 pi^2 A(t)).

    For V(x, 0) = x - x^2 the sine coefficients are b_k = 8 / (k pi)^3 for odd k, 0 for even k.
    """
    big_a = integrated_diffusivity(t)
    total = 0.0
    for k in range(1, 2 * n_terms, 2):
        kp = k * math.pi
        total += 8.0 / kp ** 3 * math.sin(kp * x) * math.exp(-kp * kp * big_a)
    return total


def solve_tridiagonal(lower, diag, upper, rhs):
    """Thomas algorithm. lower[0] and upper[-1] are ignored."""
    n = len(diag)
    c = [0.0] * n
    d = [0.0] * n
    c[0] = upper[0] / diag[0]
    d[0] = rhs[0] / diag[0]
    for i in range(1, n):
        m = diag[i] - lower[i] * c[i - 1]
        c[i] = upper[i] / m if i < n - 1 else 0.0
        d[i] = (rhs[i] - lower[i] * d[i - 1]) / m
    x = [0.0] * n
    x[-1] = d[-1]
    for i in range(n - 2, -1, -1):
        x[i] = d[i] - c[i] * x[i + 1]
    return x


def crank_nicolson(dx, dt, t_end=1.0, store_every=None):
    """March V from t=0 to t_end. Returns (x grid, V at t_end, optional snapshots).

    Trapezoid rule on the semi-discrete system dV/dt = a(t) D V, with D the centred
    second-difference operator:
        (I - dt/2 a(t_{n+1}) D) V^{n+1} = (I + dt/2 a(t_n) D) V^n
    """
    nx = int(round(1.0 / dx))
    nt = int(round(t_end / dt))
    xs = [i * dx for i in range(nx + 1)]
    v = [initial_condition(x) for x in xs]
    v[0] = v[-1] = 0.0
    snapshots = [(0.0, list(v))] if store_every else None

    m = nx - 1  # interior unknowns
    for n in range(nt):
        t0, t1 = n * dt, (n + 1) * dt
        r0 = diffusivity(t0) * dt / (2.0 * dx * dx)
        r1 = diffusivity(t1) * dt / (2.0 * dx * dx)
        rhs = [r0 * v[i - 1] + (1.0 - 2.0 * r0) * v[i] + r0 * v[i + 1] for i in range(1, nx)]
        interior = solve_tridiagonal([-r1] * m, [1.0 + 2.0 * r1] * m, [-r1] * m, rhs)
        v = [0.0] + interior + [0.0]
        if store_every and (n + 1) % store_every == 0:
            snapshots.append((t1, list(v)))
    return xs, v, snapshots


def value_at(xs, v, x):
    """Read V at x; x must lie on the grid."""
    i = int(round(x / (xs[1] - xs[0])))
    assert abs(xs[i] - x) < 1e-12, "x is not a grid node"
    return v[i]


TABLE_STEPS = [(0.1, 0.125), (0.05, 0.0625), (0.025, 0.03125), (0.0125, 0.015625)]


def convergence_table():
    exact = exact_solution(0.5, 1.0)
    rows = []
    for dx, dt in TABLE_STEPS:
        xs, v, _ = crank_nicolson(dx, dt)
        approx = value_at(xs, v, 0.5)
        rows.append((dx, dt, approx, approx - exact))
    return exact, rows


if __name__ == "__main__":
    exact, rows = convergence_table()
    print(f"Exact V(0.5, 1) = {exact:.10f}\n")
    print(f"{'dx':>8} {'dt':>10} {'V(0.5,1)':>14} {'error':>12} {'ratio':>7}")
    prev = None
    for dx, dt, approx, err in rows:
        ratio = f"{prev / err:7.3f}" if prev else ""
        print(f"{dx:>8} {dt:>10} {approx:>14.10f} {err:>12.3e} {ratio}")
        prev = err

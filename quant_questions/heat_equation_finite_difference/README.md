# Heat-Equation Finite Difference

*Source: Financial Mathematics and Modeling Practicum (QuIC Financial Technologies, 2003–2010). The problem is restated here, not quoted.*

## Problem

Solve the heat equation with a time-varying diffusion coefficient

$$
\frac{\partial V}{\partial t} = \bigl(0.16 + 0.08\sin t\bigr)\,\frac{\partial^2 V}{\partial x^2}, \qquad 0 < x < 1,
$$

with initial condition $V(x,0) = x - x^2$ and boundary conditions $V(0,t) = V(1,t) = 0$.

Discretise space with 2nd-order centred differences and step in time with the trapezoid rule, then estimate $V(0.5,\,1)$.

Report:

1. **Convergence.** Fill in $V(0.5, 1)$ for these grids:

   | $\Delta x$ | $\Delta t$ | $V(0.5, 1)$ |
   |---|---|---|
   | 0.1    | 0.125    | |
   | 0.05   | 0.0625   | |
   | 0.025  | 0.03125  | |
   | 0.0125 | 0.015625 | |

2. **Verification.** Describe the tests used to check the code is correct.

Code should be documented and attached; any language is allowed.

## Solution

### Answer

| $\Delta x$ | $\Delta t$ | $V(0.5, 1)$ | error vs exact | error ratio |
|---|---|---|---|---|
| 0.1    | 0.125    | 0.0374306601 | $4.31\times10^{-4}$ | – |
| 0.05   | 0.0625   | 0.0371069802 | $1.07\times10^{-4}$ | 4.015 |
| 0.025  | 0.03125  | 0.0370264166 | $2.68\times10^{-5}$ | 4.007 |
| 0.0125 | 0.015625 | 0.0370063178 | $6.70\times10^{-6}$ | 4.002 |

Exact value: $V(0.5, 1) = 0.0369996222$.

### Scheme

Put grid nodes at $x_i = i\,\Delta x$ and $t_n = n\,\Delta t$, and let $a(t) = 0.16 + 0.08\sin t$. The centred second difference

$$
(DV)_i = \frac{V_{i-1} - 2V_i + V_{i+1}}{\Delta x^2}
$$

turns the PDE into the system of ODEs $\dot V = a(t)\,DV$. Applying the trapezoid rule, with the coefficient evaluated at **both** ends of the step, gives

$$
\Bigl(I - \tfrac{\Delta t}{2}\,a(t_{n+1})\,D\Bigr)V^{n+1} = \Bigl(I + \tfrac{\Delta t}{2}\,a(t_n)\,D\Bigr)V^{n}.
$$

This is Crank–Nicolson. Each step solves one tridiagonal system with the Thomas algorithm, which costs $O(N_x)$. The scheme is unconditionally stable and second-order accurate in both $\Delta x$ and $\Delta t$. The grids in the table keep $\Delta t/\Delta x = 1.25$ fixed, so each row halves both steps and the error should fall by $2^2 = 4$, which is what the table shows.

### Exact solution, used for checking

Because $a$ depends only on $t$, separation of variables still works. Writing $A(t) = \int_0^t a(s)\,ds = 0.16\,t + 0.08\,(1-\cos t)$,

$$
V(x,t) = \sum_{k\ \text{odd}} \frac{8}{(k\pi)^3}\,\sin(k\pi x)\,e^{-k^2\pi^2 A(t)},
$$

where $8/(k\pi)^3$ are the sine coefficients of $x - x^2$ (they vanish for even $k$). At $t=1$ the series converges very fast. The $k=1$ term alone gives $0.03700$.

### Verification

[`test/test_solver.py`](test/test_solver.py) checks:

- The tridiagonal solver gives the right answer on a hand-solvable system.
- The Fourier series reproduces $x - x^2$ at $t = 0$.
- The boundaries stay exactly zero.
- The solution is symmetric about $x = 0.5$, as the initial data is.
- The finest grid agrees with the exact solution to within $10^{-5}$.
- The error ratio is $4 \pm 0.1$ at each refinement, confirming second order.
- The peak $V(0.5, t)$ decreases at every step, as the maximum principle requires.

## Files

| File | Contents |
|---|---|
| [`solver.py`](solver.py) | Pure-Python Crank–Nicolson solver and exact series. `python3 solver.py` prints the table. |
| [`test/test_solver.py`](test/test_solver.py) | Unit tests. From `quant_questions/`, run `python3 -m unittest discover -s heat_equation_finite_difference -t .` |
| [`index.html`](index.html) | Stand-alone visual walk-through. Open it in a browser. |

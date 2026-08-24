import time

import streamlit as st

from sudoku.generator import DIFFICULTY_GIVENS, generate
from sudoku.solver import SudokuSolver
from sudoku.sudoku import Sudoku

RANK = 3
SIZE = RANK * RANK

st.set_page_config(page_title='Sudoku', page_icon='🧩', layout='centered')

CELL_COLORS = {
    'given': '#cfd3dc',
    'user': '#5b8def',
    'single': 'rgba(63, 178, 127, 0.35)',
    'trial': 'rgba(224, 168, 59, 0.35)',
    'hint': 'rgba(216, 114, 216, 0.4)',
    'conflict': 'rgba(224, 85, 63, 0.35)',
}

st.markdown(
    """
    <style>
    .sdk-table { border-collapse: collapse; margin: 0 auto 8px auto; }
    .sdk-table td {
        width: 40px; height: 40px; text-align: center; vertical-align: middle;
        font-size: 18px; font-weight: 600; border: 1px solid #3a3d47;
    }
    .sdk-table tr:nth-child(3n+1) td { border-top: 2px solid #cfd3dc; }
    .sdk-table td:nth-child(3n+1) { border-left: 2px solid #cfd3dc; }
    .sdk-table { border: 2px solid #cfd3dc; }
    .sdk-table td[title] { cursor: help; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _candidates(grid, r, c):
    if grid[r][c]:
        return []
    used = set()
    for i in range(SIZE):
        if grid[r][i]:
            used.add(grid[r][i])
        if grid[i][c]:
            used.add(grid[i][c])
    br, bc = (r // RANK) * RANK, (c // RANK) * RANK
    for dr in range(RANK):
        for dc in range(RANK):
            v = grid[br + dr][bc + dc]
            if v:
                used.add(v)
    return [v for v in range(1, SIZE + 1) if v not in used]


def _new_grids(difficulty: str):
    puzzle = generate(rank=RANK, difficulty=difficulty)
    given = puzzle.grid.tolist()
    return given, [row[:] for row in given]


def _find_conflicts(grid):
    conflicts = set()

    def scan(cells):
        seen = {}
        for (r, c) in cells:
            v = grid[r][c]
            if not v:
                continue
            if v in seen:
                conflicts.add(seen[v])
                conflicts.add((r, c))
            else:
                seen[v] = (r, c)

    for r in range(SIZE):
        scan([(r, c) for c in range(SIZE)])
    for c in range(SIZE):
        scan([(r, c) for r in range(SIZE)])
    for br in range(RANK):
        for bc in range(RANK):
            scan([(r, c) for r in range(br * RANK, br * RANK + RANK)
                  for c in range(bc * RANK, bc * RANK + RANK)])
    return conflicts


def _render_html(grid, given, conflicts, highlight) -> str:
    rows_html = []
    for r in range(SIZE):
        cells_html = []
        for c in range(SIZE):
            value = grid[r][c]
            text = str(value) if value else '&nbsp;'
            if (r, c) in conflicts:
                color = CELL_COLORS['conflict']
            elif (r, c) in highlight:
                color = CELL_COLORS[highlight[(r, c)]]
            else:
                color = 'transparent'
            font_color = CELL_COLORS['given'] if given[r][c] else CELL_COLORS['user']
            title_attr = ''
            if not value:
                candidates = _candidates(grid, r, c)
                label = ', '.join(str(v) for v in candidates) if candidates else 'none'
                title_attr = f' title="Possible: {label}"'
            cells_html.append(
                f'<td style="background:{color};color:{font_color}"{title_attr}>{text}</td>'
            )
        rows_html.append('<tr>' + ''.join(cells_html) + '</tr>')
    return '<table class="sdk-table">' + ''.join(rows_html) + '</table>'


if 'given' not in st.session_state:
    st.session_state.given, st.session_state.current = _new_grids('medium')
    st.session_state.status = 'New puzzle ready.'
    st.session_state.highlight = {}

st.title('Sudoku')

grid_placeholder = st.empty()
status_placeholder = st.empty()


def draw():
    conflicts = _find_conflicts(st.session_state.current)
    grid_placeholder.markdown(
        _render_html(st.session_state.current, st.session_state.given, conflicts, st.session_state.highlight),
        unsafe_allow_html=True,
    )
    status_placeholder.caption(st.session_state.status)
    return conflicts


draw()
st.caption('Hover an empty cell to see its possible values.')

difficulty = st.selectbox('Difficulty', list(DIFFICULTY_GIVENS.keys()), index=1)

col_new, col_solve, col_hint, col_reset = st.columns(4)

if col_new.button('New Sudoku', use_container_width=True):
    st.session_state.given, st.session_state.current = _new_grids(difficulty)
    st.session_state.highlight = {}
    st.session_state.status = 'New puzzle ready.'
    st.rerun()

if col_solve.button('Solve step-by-step', use_container_width=True):
    conflicts = _find_conflicts(st.session_state.current)
    if conflicts:
        st.session_state.status = 'Fix the highlighted conflicts before solving.'
        st.rerun()
    else:
        sudoku = Sudoku.create(st.session_state.current)
        solver = SudokuSolver(sudoku)
        st.session_state.status = 'Thinking…'
        for coord, value, technique in solver.solve_steps():
            r, c = coord
            st.session_state.current[r][c] = value
            st.session_state.highlight = {(r, c): technique}
            draw()
            time.sleep(0.12)
        st.session_state.status = 'Solved!' if solver.solution.is_fulfilled else 'No solution found.'
        st.session_state.highlight = {}
        st.rerun()

if col_hint.button('Hint', use_container_width=True):
    conflicts = _find_conflicts(st.session_state.current)
    if conflicts:
        st.session_state.status = 'Fix the highlighted conflicts before asking for a hint.'
    else:
        sudoku = Sudoku.create(st.session_state.current)
        solver = SudokuSolver(sudoku)
        result = solver.hint()
        if result is None:
            st.session_state.status = 'No hint available — puzzle is solved or unsolvable.'
            st.session_state.highlight = {}
        else:
            coord, value, technique = result
            r, c = coord
            st.session_state.current[r][c] = value
            st.session_state.highlight = {(r, c): 'hint'}
            st.session_state.status = ('Hint: that cell only has one possible value left.'
                                        if technique == 'single'
                                        else 'Hint: took some deeper reasoning to find this one.')
    st.rerun()

if col_reset.button('Reset', use_container_width=True):
    st.session_state.current = [row[:] for row in st.session_state.given]
    st.session_state.highlight = {}
    st.session_state.status = 'Reset to the original givens.'
    st.rerun()

st.divider()
st.subheader('Enter a value')
edit_cols = st.columns(3)
row = edit_cols[0].number_input('Row', min_value=1, max_value=SIZE, value=1) - 1
col = edit_cols[1].number_input('Column', min_value=1, max_value=SIZE, value=1) - 1
value = edit_cols[2].number_input('Value (0 clears)', min_value=0, max_value=SIZE, value=0)
if st.button('Set cell'):
    if st.session_state.given[row][col]:
        st.session_state.status = "That's a given cell and can't be edited."
    else:
        st.session_state.current[row][col] = int(value)
        st.session_state.highlight = {}
        st.session_state.status = f'Set ({row + 1}, {col + 1}) to {value or "empty"}.'
    st.rerun()

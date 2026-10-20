import time
from pathlib import Path

import streamlit as st

from sudoku.generator import DIFFICULTY_GIVENS, generate
from sudoku.solver import SudokuSolver
from sudoku.sudoku import Sudoku

RANK = 3
SIZE = RANK * RANK

st.set_page_config(page_title='Sudoku', page_icon='🧩', layout='centered')

# paper-theme tokens only: its base rules (button, input, table, ...) would fight Streamlit's own widget styles
PAPER_TOKENS = Path(__file__).with_name('theme').joinpath('paper.css').read_text().split('/* base */')[0]
PAPER_TOKENS = '\n'.join(line for line in PAPER_TOKENS.splitlines() if line.strip())  # a blank line ends st.markdown's HTML block
FONTS = ('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600'
         '&family=IBM+Plex+Sans:wght@400;600&display=swap')

st.markdown(
    f"""
    <style>
    @import url('{FONTS}');
    {PAPER_TOKENS}
    .sdk-table {{ border-collapse: collapse; margin: 0 auto 8px auto; border: 2px solid var(--ink); background: var(--surface); }}
    .sdk-table td {{
        width: 40px; height: 40px; padding: 0; text-align: center; vertical-align: middle;
        font: 500 18px/1 var(--mono); font-variant-numeric: tabular-nums;
        color: var(--oxford); background: var(--surface); border: 1px solid var(--line);
    }}
    .sdk-table tr:nth-child(3n+1) td {{ border-top: 2px solid var(--ink); }}
    .sdk-table td:nth-child(3n+1) {{ border-left: 2px solid var(--ink); }}
    .sdk-table td.given {{ background: var(--code); color: var(--ink); font-weight: 600; }}
    .sdk-table td.fill-single {{ background: var(--teal-soft); }}
    .sdk-table td.fill-trial {{ background: var(--mandarin-soft); }}
    .sdk-table td.fill-hint {{ background: var(--oxford-soft); }}
    .sdk-table td.conflict {{ background: var(--claret-soft); color: var(--claret); }}
    .sdk-table td[title] {{ cursor: help; }}
    .sdk-legend {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 4px 14px;
                   font: 400 12px/1.4 var(--sans); color: var(--muted); margin-bottom: 8px; }}
    .sdk-legend i {{ display: inline-block; width: 11px; height: 11px; margin-right: 5px; vertical-align: -1px;
                     border: 1px solid var(--line); }}
    </style>
    """,
    unsafe_allow_html=True,
)

LEGEND = ('<div class="sdk-legend">'
          '<span><i style="background:var(--code)"></i>Given</span>'
          '<span><i style="background:var(--oxford);border-color:var(--oxford)"></i>Your entry</span>'
          '<span><i style="background:var(--teal-soft)"></i>Logical fill</span>'
          '<span><i style="background:var(--mandarin-soft)"></i>Guessed fill</span>'
          '<span><i style="background:var(--oxford-soft)"></i>Hint</span>'
          '<span><i style="background:var(--claret-soft)"></i>Conflict</span>'
          '</div>')


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
            classes = []
            if given[r][c]:
                classes.append('given')
            if (r, c) in conflicts:
                classes.append('conflict')
            elif (r, c) in highlight:
                classes.append('fill-' + highlight[(r, c)])
            class_attr = f' class="{" ".join(classes)}"' if classes else ''
            title_attr = ''
            if not value:
                candidates = _candidates(grid, r, c)
                label = ', '.join(str(v) for v in candidates) if candidates else 'none'
                title_attr = f' title="Possible: {label}"'
            cells_html.append(
                f'<td{class_attr}{title_attr}>{text}</td>'
            )
        rows_html.append('<tr>' + ''.join(cells_html) + '</tr>')
    return '<table class="sdk-table">' + ''.join(rows_html) + '</table>' + LEGEND


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

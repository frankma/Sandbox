import re
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from tkinter import ttk

from sudoku.generator import DIFFICULTY_GIVENS, generate
from sudoku.solver import SudokuSolver
from sudoku.sudoku import Sudoku

RANK = 3
SIZE = RANK * RANK

PAPER_CSS = Path(__file__).resolve().parents[1].joinpath('theme', 'paper.css')


def _paper_tokens() -> dict:
    """The light :root token block of theme/paper.css (tkinter has no dark-mode switch, so light only)."""
    block = PAPER_CSS.read_text().split('@media')[0]
    return dict(re.findall(r'--([\w-]+):\s*([^;]+);', block))


TOKENS = _paper_tokens()

# paper-theme roles for the grid, matching the web and Streamlit versions
COLORS = {
    'bg': TOKENS['bg'],
    'surface': TOKENS['surface'],
    'ink': TOKENS['ink'],
    'muted': TOKENS['muted'],
    'line': TOKENS['line'],
    'axis': TOKENS['axis'],
    'given_bg': TOKENS['code'],
    'user': TOKENS['oxford'],
    'single': TOKENS['teal-soft'],
    'trial': TOKENS['mandarin-soft'],
    'hint': TOKENS['oxford-soft'],
    'conflict': TOKENS['claret-soft'],
    'conflict_fg': TOKENS['claret'],
}


def _font_family(stack: str) -> str:
    """First family of a CSS font stack that Tk can find (needs a Tk root to exist)."""
    available = set(tkfont.families())
    names = [name.strip().strip('\'"') for name in stack.split(',')]
    return next((n for n in names if n in available), 'TkDefaultFont')


class Fonts:
    def __init__(self):
        display = _font_family(TOKENS['display'])
        sans = _font_family(TOKENS['sans'])
        mono = _font_family(TOKENS['mono'])
        self.title = (display, 26, 'bold')
        self.label = (sans, 12)
        self.button = (sans, 12, 'bold')
        self.cell = (mono, 17)
        self.cell_given = (mono, 17, 'bold')
        self.tip = (mono, 11)
        self.tip_active = (mono, 11, 'bold')


class CandidateTooltip:
    def __init__(self, root: tk.Tk, fonts: Fonts):
        self.root = root
        self.fonts = fonts
        self.window = None

    def show(self, x: int, y: int, candidates):
        self.hide()
        self.window = tk.Toplevel(self.root)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f'+{x}+{y}')
        frame = tk.Frame(self.window, bg=COLORS['surface'], bd=0, padx=4, pady=4,
                          highlightbackground=COLORS['line'], highlightthickness=1)
        frame.pack()
        for d in range(1, SIZE + 1):
            row, col = divmod(d - 1, RANK)
            active = d in candidates
            tk.Label(frame, text=str(d), width=2, bg=COLORS['surface'],
                     fg=COLORS['user'] if active else COLORS['axis'],
                     font=self.fonts.tip_active if active else self.fonts.tip
                     ).grid(row=row, column=col, padx=1, pady=1)

    def hide(self):
        if self.window is not None:
            self.window.destroy()
            self.window = None


class SudokuGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Sudoku')
        self.root.configure(bg=COLORS['bg'])
        self.fonts = Fonts()
        self._configure_ttk()

        self.given_grid = [[0] * SIZE for _ in range(SIZE)]
        self.current_grid = [[0] * SIZE for _ in range(SIZE)]
        self.entries = {}
        self.vars = {}
        self.busy = False
        self.tooltip = CandidateTooltip(root, self.fonts)

        self._build_widgets()
        self.new_puzzle()

    def _configure_ttk(self):
        # 'clam' is the built-in ttk theme that honours colours on every platform (aqua ignores them on macOS)
        style = ttk.Style(self.root)
        style.theme_use('clam')
        flat = dict(borderwidth=1, relief='flat', focusthickness=0)
        style.configure('TButton', font=self.fonts.button, padding=(12, 7), background=COLORS['surface'],
                        foreground=COLORS['ink'], bordercolor=COLORS['line'], lightcolor=COLORS['surface'],
                        darkcolor=COLORS['surface'], **flat)
        style.map('TButton', bordercolor=[('active', COLORS['ink'])], background=[('active', COLORS['surface'])],
                  foreground=[('disabled', COLORS['axis'])])
        style.configure('Primary.TButton', background=COLORS['ink'], foreground=COLORS['surface'],
                        bordercolor=COLORS['ink'], lightcolor=COLORS['ink'], darkcolor=COLORS['ink'])
        style.map('Primary.TButton', background=[('disabled', COLORS['line']), ('active', COLORS['ink'])],
                  foreground=[('disabled', COLORS['surface'])])
        style.configure('TCombobox', fieldbackground=COLORS['bg'], background=COLORS['surface'],
                        foreground=COLORS['ink'], bordercolor=COLORS['line'], arrowcolor=COLORS['ink'],
                        lightcolor=COLORS['bg'], darkcolor=COLORS['bg'], padding=(6, 4))
        style.map('TCombobox', fieldbackground=[('readonly', COLORS['bg'])],
                  selectbackground=[('readonly', COLORS['bg'])], selectforeground=[('readonly', COLORS['ink'])])
        self.root.option_add('*TCombobox*Listbox.background', COLORS['surface'])
        self.root.option_add('*TCombobox*Listbox.foreground', COLORS['ink'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', COLORS['hint'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', COLORS['ink'])
        self.root.option_add('*TCombobox*Listbox.font', self.fonts.label)
        style.configure('Horizontal.TScale', background=COLORS['user'], troughcolor=COLORS['line'],
                        bordercolor=COLORS['bg'], lightcolor=COLORS['user'], darkcolor=COLORS['user'])

    def _build_widgets(self):
        # 4px ink rule above the headline, as on the paper-theme pages
        tk.Frame(self.root, bg=COLORS['ink'], height=4).pack(fill='x', padx=14, pady=(14, 0))
        title = tk.Label(self.root, text='Sudoku', font=self.fonts.title, bg=COLORS['bg'], fg=COLORS['ink'])
        title.pack(anchor='w', padx=14, pady=(6, 6))

        # ink rules between 3x3 boxes, hairlines between cells
        grid_outer = tk.Frame(self.root, bg=COLORS['ink'], padx=1, pady=1)
        grid_outer.pack(padx=14, pady=6)

        block_frames = {}
        for br in range(RANK):
            for bc in range(RANK):
                block = tk.Frame(grid_outer, bg=COLORS['line'])
                block.grid(row=br, column=bc, padx=1, pady=1)
                block_frames[(br, bc)] = block

        for r in range(SIZE):
            for c in range(SIZE):
                block = block_frames[(r // RANK, c // RANK)]
                var = tk.StringVar()
                vcmd = (self.root.register(self._validate_input), '%P')
                entry = tk.Entry(block, textvariable=var, width=2, justify='center',
                                  font=self.fonts.cell, relief='flat', bd=0, highlightthickness=0,
                                  bg=COLORS['surface'], fg=COLORS['user'],
                                  insertbackground=COLORS['user'],
                                  validate='key', validatecommand=vcmd)
                entry.grid(row=r % RANK, column=c % RANK, padx=(0, 1) if c % RANK < RANK - 1 else 0,
                           pady=(0, 1) if r % RANK < RANK - 1 else 0, ipady=6, ipadx=2)
                entry.bind('<FocusOut>', lambda e, r=r, c=c: self._on_cell_changed(r, c))
                entry.bind('<KeyRelease>', lambda e, r=r, c=c: self._on_cell_changed(r, c))
                entry.bind('<Enter>', lambda e, r=r, c=c: self._on_cell_hover(r, c, e))
                entry.bind('<Leave>', lambda e: self.tooltip.hide())
                self.entries[(r, c)] = entry
                self.vars[(r, c)] = var

        self.status_var = tk.StringVar(value='')
        status = tk.Label(self.root, textvariable=self.status_var, bg=COLORS['bg'],
                           fg=COLORS['muted'], font=self.fonts.label)
        status.pack(pady=(4, 2))

        legend = tk.Frame(self.root, bg=COLORS['bg'])
        legend.pack(pady=(0, 8))
        for swatch, text in ((COLORS['given_bg'], 'Given'), (COLORS['single'], 'Logical fill'),
                             (COLORS['trial'], 'Guessed fill'), (COLORS['hint'], 'Hint'),
                             (COLORS['conflict'], 'Conflict')):
            tk.Frame(legend, bg=swatch, width=11, height=11, highlightbackground=COLORS['line'],
                     highlightthickness=1).pack(side='left', padx=(8, 4))
            tk.Label(legend, text=text, bg=COLORS['bg'], fg=COLORS['muted'],
                     font=self.fonts.label).pack(side='left')

        controls = tk.Frame(self.root, bg=COLORS['bg'])
        controls.pack(pady=(0, 14))

        row1 = tk.Frame(controls, bg=COLORS['bg'])
        row1.pack(pady=3)
        self.difficulty_var = tk.StringVar(value='medium')
        difficulty_menu = ttk.Combobox(row1, textvariable=self.difficulty_var, state='readonly',
                                        values=list(DIFFICULTY_GIVENS.keys()), width=10, font=self.fonts.label)
        difficulty_menu.pack(side='left', padx=4)
        self.new_btn = ttk.Button(row1, text='New Sudoku', style='Primary.TButton', command=self.new_puzzle)
        self.new_btn.pack(side='left', padx=4)

        row2 = tk.Frame(controls, bg=COLORS['bg'])
        row2.pack(pady=3)
        self.solve_btn = ttk.Button(row2, text='Solve step-by-step', command=self.solve_step_by_step)
        self.solve_btn.pack(side='left', padx=4)
        tk.Label(row2, text='Speed', bg=COLORS['bg'], fg=COLORS['muted'],
                 font=self.fonts.label).pack(side='left', padx=(10, 4))
        # the slider reads fast on the right; the delay is its mirror image
        self.speed_var = tk.IntVar(value=410 - 120)
        speed_scale = ttk.Scale(row2, from_=10, to=400, orient='horizontal', variable=self.speed_var,
                                length=120)
        speed_scale.pack(side='left')

        row3 = tk.Frame(controls, bg=COLORS['bg'])
        row3.pack(pady=3)
        self.hint_btn = ttk.Button(row3, text='Hint', command=self.hint)
        self.hint_btn.pack(side='left', padx=4)
        self.reset_btn = ttk.Button(row3, text='Reset', command=self.reset)
        self.reset_btn.pack(side='left', padx=4)

    def _validate_input(self, proposed: str) -> bool:
        return proposed == '' or (proposed.isdigit() and 1 <= int(proposed) <= SIZE and len(proposed) == 1)

    def _set_busy(self, busy: bool):
        self.busy = busy
        state = 'disabled' if busy else 'normal'
        for widget in (self.new_btn, self.solve_btn, self.hint_btn, self.reset_btn):
            widget.config(state=state)
        if busy:
            self.tooltip.hide()

    def _on_cell_changed(self, r, c):
        if self.given_grid[r][c]:
            return
        text = self.vars[(r, c)].get()
        self.current_grid[r][c] = int(text) if text else 0
        self._refresh_conflicts()

    def _candidates(self, r, c):
        if self.current_grid[r][c]:
            return []
        used = set()
        for i in range(SIZE):
            if self.current_grid[r][i]:
                used.add(self.current_grid[r][i])
            if self.current_grid[i][c]:
                used.add(self.current_grid[i][c])
        br, bc = (r // RANK) * RANK, (c // RANK) * RANK
        for dr in range(RANK):
            for dc in range(RANK):
                v = self.current_grid[br + dr][bc + dc]
                if v:
                    used.add(v)
        return [v for v in range(1, SIZE + 1) if v not in used]

    def _on_cell_hover(self, r, c, event):
        if self.busy or self.given_grid[r][c] or self.current_grid[r][c]:
            self.tooltip.hide()
            return
        candidates = self._candidates(r, c)
        widget = event.widget
        x = widget.winfo_rootx() + widget.winfo_width() + 6
        y = widget.winfo_rooty()
        self.tooltip.show(x, y, candidates)

    def _find_conflicts(self):
        conflicts = set()

        def scan(cells):
            seen = {}
            for (r, c) in cells:
                v = self.current_grid[r][c]
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

    def _refresh_conflicts(self):
        conflicts = self._find_conflicts()
        for (r, c), entry in self.entries.items():
            is_given = self.given_grid[r][c] != 0
            if (r, c) in conflicts:
                bg, fg = COLORS['conflict'], COLORS['conflict_fg']
            elif is_given:
                bg, fg = COLORS['given_bg'], COLORS['ink']
            else:
                bg, fg = COLORS['surface'], COLORS['user']
            # given cells are read-only, and a read-only Entry draws readonlybackground instead of bg
            entry.config(bg=bg, readonlybackground=bg, fg=fg)
        return conflicts

    def _render(self):
        for r in range(SIZE):
            for c in range(SIZE):
                is_given = self.given_grid[r][c] != 0
                value = self.current_grid[r][c]
                var = self.vars[(r, c)]
                var.set(str(value) if value else '')
                entry = self.entries[(r, c)]
                entry.config(font=self.fonts.cell_given if is_given else self.fonts.cell,
                              state='readonly' if is_given else 'normal')
        self._refresh_conflicts()

    def _paint_cell(self, r, c, technique):
        self.entries[(r, c)].config(bg=COLORS[technique])

    def new_puzzle(self):
        if self.busy:
            return
        self.tooltip.hide()
        self.status_var.set('Generating…')
        self.root.update_idletasks()
        puzzle = generate(rank=RANK, difficulty=self.difficulty_var.get())
        self.given_grid = puzzle.grid.tolist()
        self.current_grid = [row[:] for row in self.given_grid]
        self._render()
        self.status_var.set('New puzzle ready.')

    def solve_step_by_step(self):
        if self.busy:
            return
        if self._refresh_conflicts():
            self.status_var.set('Fix the highlighted conflicts before solving.')
            return
        try:
            sudoku = Sudoku.create(self.current_grid)
        except ValueError as exc:
            self.status_var.set(str(exc))
            return
        solver = SudokuSolver(sudoku)
        steps = list(solver.solve_steps())
        if not solver.solution.is_fulfilled:
            self.status_var.set('No solution found from the current entries.')
            return
        self._set_busy(True)
        self.status_var.set('Solving…')
        self._animate_steps(steps, 0, solver)

    def _animate_steps(self, steps, index, solver):
        if index >= len(steps):
            self._set_busy(False)
            self.status_var.set('Solved!')
            return
        coord, value, technique = steps[index]
        r, c = coord
        self.current_grid[r][c] = value
        self.vars[(r, c)].set(str(value))
        self._paint_cell(r, c, technique)
        self.root.after(410 - self.speed_var.get(),lambda: self._animate_steps(steps, index + 1, solver))

    def hint(self):
        if self.busy:
            return
        if self._refresh_conflicts():
            self.status_var.set('Fix the highlighted conflicts before asking for a hint.')
            return
        try:
            sudoku = Sudoku.create(self.current_grid)
        except ValueError as exc:
            self.status_var.set(str(exc))
            return
        solver = SudokuSolver(sudoku)
        result = solver.hint()
        if result is None:
            self.status_var.set('No hint available — puzzle is solved or unsolvable.')
            return
        coord, value, technique = result
        r, c = coord
        self.current_grid[r][c] = value
        self.vars[(r, c)].set(str(value))
        self._paint_cell(r, c, 'hint')
        self.status_var.set('Hint: that cell only has one possible value left.' if technique == 'single'
                             else 'Hint: took some deeper reasoning to find this one.')

    def reset(self):
        if self.busy:
            return
        self.current_grid = [row[:] for row in self.given_grid]
        self._render()
        self.status_var.set('Reset to the original givens.')


def main():
    root = tk.Tk()
    SudokuGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

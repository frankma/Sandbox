import tkinter as tk
from tkinter import ttk

from sudoku.generator import DIFFICULTY_GIVENS, generate
from sudoku.solver import SudokuSolver
from sudoku.sudoku import Sudoku

RANK = 3
SIZE = RANK * RANK

COLORS = {
    'bg': '#1b1d23',
    'panel': '#24262e',
    'border': '#cfd3dc',
    'given': '#cfd3dc',
    'user': '#5b8def',
    'single': '#2f6b4f',
    'trial': '#8a672a',
    'hint': '#6e3a6e',
    'conflict': '#7a3129',
    'default_bg': '#2c2f38',
}


class CandidateTooltip:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.window = None

    def show(self, x: int, y: int, candidates):
        self.hide()
        self.window = tk.Toplevel(self.root)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f'+{x}+{y}')
        frame = tk.Frame(self.window, bg=COLORS['panel'], bd=1,
                          highlightbackground=COLORS['border'], highlightthickness=1)
        frame.pack()
        for d in range(1, SIZE + 1):
            row, col = divmod(d - 1, RANK)
            active = d in candidates
            tk.Label(frame, text=str(d), width=2, bg=COLORS['panel'],
                     fg=COLORS['user'] if active else '#565b66',
                     font=('Helvetica', 11, 'bold' if active else 'normal')
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

        self.given_grid = [[0] * SIZE for _ in range(SIZE)]
        self.current_grid = [[0] * SIZE for _ in range(SIZE)]
        self.entries = {}
        self.vars = {}
        self.busy = False
        self.tooltip = CandidateTooltip(root)

        self._build_widgets()
        self.new_puzzle()

    def _build_widgets(self):
        title = tk.Label(self.root, text='Sudoku', font=('Helvetica', 20, 'bold'),
                          bg=COLORS['bg'], fg=COLORS['border'])
        title.pack(pady=(14, 6))

        grid_outer = tk.Frame(self.root, bg=COLORS['border'], bd=2)
        grid_outer.pack(padx=14, pady=6)

        block_frames = {}
        for br in range(RANK):
            for bc in range(RANK):
                block = tk.Frame(grid_outer, bg=COLORS['border'], padx=1, pady=1)
                block.grid(row=br, column=bc, padx=1, pady=1)
                block_frames[(br, bc)] = block

        for r in range(SIZE):
            for c in range(SIZE):
                block = block_frames[(r // RANK, c // RANK)]
                var = tk.StringVar()
                vcmd = (self.root.register(self._validate_input), '%P')
                entry = tk.Entry(block, textvariable=var, width=2, justify='center',
                                  font=('Helvetica', 16), relief='flat',
                                  bg=COLORS['default_bg'], fg=COLORS['user'],
                                  insertbackground=COLORS['user'],
                                  validate='key', validatecommand=vcmd)
                entry.grid(row=r % RANK, column=c % RANK, padx=1, pady=1, ipady=4)
                entry.bind('<FocusOut>', lambda e, r=r, c=c: self._on_cell_changed(r, c))
                entry.bind('<KeyRelease>', lambda e, r=r, c=c: self._on_cell_changed(r, c))
                entry.bind('<Enter>', lambda e, r=r, c=c: self._on_cell_hover(r, c, e))
                entry.bind('<Leave>', lambda e: self.tooltip.hide())
                self.entries[(r, c)] = entry
                self.vars[(r, c)] = var

        self.status_var = tk.StringVar(value='')
        status = tk.Label(self.root, textvariable=self.status_var, bg=COLORS['bg'],
                           fg='#9aa0ad', font=('Helvetica', 11))
        status.pack(pady=(4, 8))

        controls = tk.Frame(self.root, bg=COLORS['bg'])
        controls.pack(pady=(0, 12))

        row1 = tk.Frame(controls, bg=COLORS['bg'])
        row1.pack(pady=3)
        self.difficulty_var = tk.StringVar(value='medium')
        difficulty_menu = ttk.Combobox(row1, textvariable=self.difficulty_var, state='readonly',
                                        values=list(DIFFICULTY_GIVENS.keys()), width=10)
        difficulty_menu.pack(side='left', padx=4)
        self.new_btn = tk.Button(row1, text='New Sudoku', command=self.new_puzzle)
        self.new_btn.pack(side='left', padx=4)

        row2 = tk.Frame(controls, bg=COLORS['bg'])
        row2.pack(pady=3)
        self.solve_btn = tk.Button(row2, text='Solve step-by-step', command=self.solve_step_by_step)
        self.solve_btn.pack(side='left', padx=4)
        tk.Label(row2, text='Speed', bg=COLORS['bg'], fg='#9aa0ad').pack(side='left', padx=(10, 2))
        self.speed_var = tk.IntVar(value=120)
        speed_scale = tk.Scale(row2, from_=10, to=400, orient='horizontal', variable=self.speed_var,
                                bg=COLORS['bg'], fg='#9aa0ad', highlightthickness=0, length=120,
                                showvalue=False)
        speed_scale.pack(side='left')

        row3 = tk.Frame(controls, bg=COLORS['bg'])
        row3.pack(pady=3)
        self.hint_btn = tk.Button(row3, text='Hint', command=self.hint)
        self.hint_btn.pack(side='left', padx=4)
        self.reset_btn = tk.Button(row3, text='Reset', command=self.reset)
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
            if (r, c) in conflicts:
                entry.config(bg=COLORS['conflict'])
            elif self.given_grid[r][c]:
                entry.config(bg=COLORS['panel'])
            else:
                entry.config(bg=COLORS['default_bg'])
        return conflicts

    def _render(self):
        for r in range(SIZE):
            for c in range(SIZE):
                is_given = self.given_grid[r][c] != 0
                value = self.current_grid[r][c]
                var = self.vars[(r, c)]
                var.set(str(value) if value else '')
                entry = self.entries[(r, c)]
                entry.config(fg=COLORS['given'] if is_given else COLORS['user'],
                              state='readonly' if is_given else 'normal',
                              readonlybackground=COLORS['panel'])
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
        self.root.after(self.speed_var.get(), lambda: self._animate_steps(steps, index + 1, solver))

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

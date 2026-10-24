# Sandbox

Small, self-contained projects. Each top-level folder stands alone: no folder imports another, so any one can be copied out and used on its own.

| Folder | What it is | Dependencies |
|---|---|---|
| [bet/](bet/) | Binary expression tree: build, print and evaluate arithmetic expressions | none |
| [maze/](maze/) | Grid maze and a path solver | numpy |
| [poker/](poker/) | Texas hold'em: hand evaluator, Monte Carlo strategy, odds advisor, terminal game | none |
| [sudoku/](sudoku/) | Sudoku solver and generator, with tkinter, Flask and Streamlit front-ends | numpy (+ flask / streamlit, see [requirements](sudoku/requirements.txt)) |
| [finding_fox/](finding_fox/) | Word-search game, a single HTML page | none (open in a browser) |
| [the_threshold/](the_threshold/) | Percolation game: breadth-first flood through an N×N grid, a Monte Carlo threshold curve, and a rot mode (random rot vs targeted attack, with a break-fraction histogram around 1 − p_c), a single HTML page | none (open in a browser) |
| [guandan/](guandan/) | GuanDan (掼蛋) partnership climbing game: a primer page ([tutorial.html](guandan/tutorial.html)) and a practice table where you play with a computer partner against two computer opponents, with a coach suggesting your best play | none (open in a browser) |
| [quant_questions/](quant_questions/) | Quant brain teasers, each with a write-up, solver, tests and visual page | none |

## Running

Run commands from the repo root.

```bash
python -m poker.cli                       # play hold'em in the terminal
python -m sudoku.gui_app                  # tkinter sudoku
python -m sudoku.webapp.app               # Flask sudoku on http://localhost:5050
streamlit run sudoku/streamlit_app.py     # Streamlit sudoku
open finding_fox/index.html
open the_threshold/index.html
open guandan/tutorial.html
open guandan/index.html
```

## Tests

```bash
python -m pytest
```

Or test one project at a time, e.g. `python -m pytest poker`.

## Layout conventions

- One folder per project: code at the top, tests in `test/`, and an `index.html` for any visual page.
- HTML pages inline their styling (the paper theme), so each page opens on its own as a file.
- A project with third-party dependencies lists them in its own `requirements.txt`.

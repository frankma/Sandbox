# Sandbox

Small, self-contained projects. Each top-level folder stands alone: no folder imports another, so any one can be copied out and used on its own.

The visual pages are published with GitHub Pages at <https://frankma.github.io/Sandbox/>, with [index.html](index.html) at the repo root as the front page linking to each one.

Once a project has a proper home in another repo, it moves out of the sandbox. The card games (hold'em and GuanDan) now live in the Finance repo under `src/CardGames`.

| Folder | What it is | Dependencies |
|---|---|---|
| [bet/](bet/) | Binary expression tree: build, print and evaluate arithmetic expressions | none |
| [maze/](maze/) | Grid maze and a path solver | numpy |
| [sudoku/](sudoku/) | Sudoku solver and generator, with tkinter, Flask and Streamlit front-ends | numpy (+ flask / streamlit, see [requirements](sudoku/requirements.txt)) |
| [finding_fox/](finding_fox/) | Word-search game, a single HTML page | none (open in a browser) |
| [the_threshold/](the_threshold/) | Percolation game: breadth-first flood through an N×N grid, a Monte Carlo threshold curve, and a rot mode (random rot vs targeted attack, with a break-fraction histogram around 1 − p_c), a single HTML page | none (open in a browser) |
| [quant_questions/](quant_questions/) | Quant brain teasers, each with a write-up, solver, tests and visual page | none |

## Running

Run commands from the repo root.

```bash
python -m sudoku.gui_app                  # tkinter sudoku
python -m sudoku.webapp.app               # Flask sudoku on http://localhost:5050
streamlit run sudoku/streamlit_app.py     # Streamlit sudoku
open finding_fox/index.html
open the_threshold/index.html
```

## Tests

```bash
python -m pytest
```

Or test one project at a time, e.g. `python -m pytest sudoku`.

## Layout conventions

- One folder per project: code at the top, tests in `test/`, and an `index.html` for any visual page.
- A new visual page gets a line in the front page, [index.html](index.html), so it shows up on GitHub Pages. `.nojekyll` makes Pages serve the files as they are.
- HTML pages inline their styling, so each page opens on its own as a file. The look is Kinari (the `my-theme` skill): [kinari.css](kinari.css) is the one copy in the repo, pasted first into each page's `<style>`, and the Sudoku Tk and Streamlit apps read their colours from it.
- A project with third-party dependencies lists them in its own `requirements.txt`.

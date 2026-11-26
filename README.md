# Sandbox

Small, self-contained projects. Each top-level folder stands alone: no folder imports another, so any one can be copied out and used on its own.

The visual pages are published with GitHub Pages at <https://frankma.github.io/Sandbox/>, with [index.html](index.html) at the repo root as the front page linking to each one.

Once a project has a proper home in another repo, it moves out of the sandbox. The card games (hold'em and GuanDan) now live in the Finance repo under `src/CardGames`.

| Folder | What it is | Dependencies |
|---|---|---|
| [bet/](bet/) | Binary expression tree: build, print and evaluate arithmetic expressions | none |
| [maze/](maze/) | Grid maze and a path solver | numpy |
| [games/](games/) | Games: [Sudoku](games/sudoku/) (solver and generator, with tkinter, Flask and Streamlit front-ends) and [Finding FOX](games/finding_fox/) (a word-search page) | Sudoku: numpy (+ flask / streamlit, see [requirements](games/sudoku/requirements.txt)) |
| [quant_problems/](quant_problems/) | Quant problems, each with a write-up and visual page, most with a solver and tests; includes [The Threshold](quant_problems/the_threshold/), a percolation simulation | none |
| [game_theory/](game_theory/) | Game-theory problems, each with a write-up, solver, tests and visual page | none |

## Running

The Sudoku apps run from `games/`, where `sudoku` is the package name:

```bash
cd games && python -m sudoku.gui_app                  # tkinter sudoku
cd games && python -m sudoku.webapp.app               # Flask sudoku on http://localhost:5050
streamlit run games/sudoku/streamlit_app.py           # Streamlit sudoku, from the repo root
open games/finding_fox/index.html
open quant_problems/the_threshold/index.html
```

## Tests

```bash
python -m pytest
```

Or test one project at a time, e.g. `python -m pytest games/sudoku`.

## Layout conventions

- Folders follow the front page's sections: `games/`, `quant_problems/` and `game_theory/`, with one folder per project inside. `bet/` and `maze/` have no page, so they stay at the top level.
- In each project folder: code at the top, tests in `test/`, and an `index.html` for any visual page. A project's tests import it by its own folder name, so run them from the section folder (or with `python -m pytest` from the root).
- A new visual page gets a line in the front page, [index.html](index.html), so it shows up on GitHub Pages. `.nojekyll` makes Pages serve the files as they are.
- HTML pages inline their styling, so each page opens on its own as a file. The look is Kinari (the `my-theme` skill): [kinari.css](kinari.css) is the one copy in the repo, pasted first into each page's `<style>`, and the Sudoku Tk and Streamlit apps read their colours from it.
- A project with third-party dependencies lists them in its own `requirements.txt`.

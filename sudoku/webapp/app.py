import logging

import numpy as np
from flask import Flask, jsonify, render_template, request

from sudoku.generator import DIFFICULTY_GIVENS, generate
from sudoku.solver import SudokuSolver
from sudoku.sudoku import Sudoku

logger = logging.getLogger(__name__)

app = Flask(__name__)

RANK = 3


def _sudoku_from_payload(payload) -> Sudoku:
    grid = np.array(payload['grid'], dtype=int)
    return Sudoku.create(grid)


@app.route('/')
def index():
    return render_template('index.html', difficulties=list(DIFFICULTY_GIVENS.keys()), rank=RANK)


@app.route('/api/new', methods=['POST'])
def api_new():
    difficulty = (request.get_json(silent=True) or {}).get('difficulty', 'medium')
    puzzle = generate(rank=RANK, difficulty=difficulty)
    return jsonify({'grid': puzzle.grid.tolist(), 'size': puzzle.size})


@app.route('/api/solve_steps', methods=['POST'])
def api_solve_steps():
    payload = request.get_json(force=True)
    try:
        sudoku = _sudoku_from_payload(payload)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    solver = SudokuSolver(sudoku)
    steps = [{'row': int(coord[0]), 'col': int(coord[1]), 'value': int(value), 'technique': technique}
              for coord, value, technique in solver.solve_steps()]
    return jsonify({'steps': steps, 'solved': bool(solver.solution.is_fulfilled),
                     'grid': solver.solution.grid.tolist()})


@app.route('/api/hint', methods=['POST'])
def api_hint():
    payload = request.get_json(force=True)
    try:
        sudoku = _sudoku_from_payload(payload)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    solver = SudokuSolver(sudoku)
    result = solver.hint()
    if result is None:
        return jsonify({'hint': None})
    coord, value, technique = result
    return jsonify({'hint': {'row': int(coord[0]), 'col': int(coord[1]), 'value': int(value),
                              'technique': technique}})


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=5050)

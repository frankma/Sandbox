# Coin Toss 1: Four Coins on a Spinning Table

## Problem

Four coins sit at the corners of a square on a round table, each heads or tails at random. You can't see them. Each turn you say which coins to flip (one or several, by where they sit in front of you) and they are flipped. If all four then show the same face, all heads or all tails, you win and the game stops. Otherwise the table turns to an unknown angle and you go again. Find a strategy that is guaranteed to win.

## Answer

Seven moves, stopping as soon as you win:

| Move | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| Flip | D | A | D | S | D | A | D |

- **D**: two diagonally opposite coins
- **A**: two neighbouring coins
- **S**: any one coin

## Why

Because the table turns and either all-heads or all-tails wins, only the pattern matters. A table that hasn't won has one of three shapes, up to turning and swapping heads with tails:

| Shape | Example | Layouts | after D | after A | after S |
|---|---|---|---|---|---|
| One | HTTT | 8 of 14 | One | One | Win, Adjacent or Diagonal |
| Adjacent | HHTT | 4 of 14 | Adjacent | Win or Diagonal | One |
| Diagonal | HTHT | 2 of 14 | **Win** | Adjacent | One |

Flipping three coins is the same as flipping one and swapping heads with tails, and flipping all four changes nothing, so D, A and S are the only moves.

- **D A D wins any 2–2 table** (Adjacent or Diagonal) and leaves One alone. Diagonal: D wins. Adjacent: D keeps it Adjacent, A wins or makes it Diagonal, D wins.
- **If D A D hasn't won, the table is One.** S then wins or makes a 2–2 table, and a second D A D finishes it.

Shapes still possible after each move:

| | start | D | A | D | S | D | A | D |
|---|---|---|---|---|---|---|---|---|
| One | ● | ● | ● | ● | | | | |
| Adjacent | ● | ● | | | ● | ● | | |
| Diagonal | ● | | ● | | ● | | ● | |

**Seven is the minimum.** A breadth-first search over everything you could know, trying all 15 ways to choose coins each turn, finds no shorter plan. Among plans made of D, A and S, D A D S D A D is the only seven-move plan that always wins.

Over all 16 starting tables and all $4^7$ sequences of turns, the plan needs 0, 1, …, 7 moves, each in exactly one game in eight: 3.5 moves on average.

## Files

| File | Contents |
|---|---|
| [`solver.py`](solver.py) | Rotations, shapes, belief tracking, the breadth-first search and a game player. `python3 solver.py` prints the plan and its trace. |
| [`test/test_solver.py`](test/test_solver.py) | Unit tests. From `quant_questions/coin_toss/`, run `python3 -m unittest discover -s rotating_table -t .` |
| [`index.html`](index.html) | Interactive page: play blind on a spinning table, watch which shapes are still possible, and test the plan against every case. |

"""Honor or Grab: an n-team repeated social dilemma with random bonus rounds.

Each round every team decides, separately for each other team, whether to HONOR or
GRAB that deal. The round is an n x n decision matrix: D[i][j] is team i's choice
toward team j (the diagonal is unused). Each pair (i, j) settles its deal from
D[i][j] and D[j][i]:

    both honor      +6 / +6
    grab vs honor  +14 / -6
    both grab       -4 / -4

A team's round score is the sum over its deals. Unanimous matrices override the
sum: every decision GRAB -> -12 each, every decision HONOR -> +15 each.
A bonus round (announced before choices) multiplies every score by the multiplier.

Run `python3 solver.py` for the stage-game analysis and a strategy tournament.
"""
import random
from dataclasses import dataclass, field
from itertools import combinations_with_replacement

HONOR, GRAB = "H", "G"


@dataclass(frozen=True)
class Rules:
    teams: int = 4
    rounds: int = 5
    multiplier: float = 3.0
    bonus_chance: float = 0.25
    both_honor: float = 6.0
    grab_vs_honor: float = 14.0
    honor_vs_grab: float = -6.0
    both_grab: float = -4.0
    all_grab: float = -12.0
    all_honor: float = 15.0


def pair_payoff(mine, theirs, rules):
    if mine == HONOR:
        return rules.both_honor if theirs == HONOR else rules.honor_vs_grab
    return rules.grab_vs_honor if theirs == HONOR else rules.both_grab


def decisions(matrix):
    """All off-diagonal decisions of a matrix."""
    return [c for i, row in enumerate(matrix) for j, c in enumerate(row) if i != j]


def round_scores(matrix, rules, bonus=False):
    """Scores for one round given the n x n decision matrix."""
    n = len(matrix)
    flat = decisions(matrix)
    if all(c == GRAB for c in flat):
        base = [rules.all_grab] * n
    elif all(c == HONOR for c in flat):
        base = [rules.all_honor] * n
    else:
        base = [sum(pair_payoff(matrix[i][j], matrix[j][i], rules) for j in range(n) if j != i)
                for i in range(n)]
    factor = rules.multiplier if bonus else 1.0
    return [s * factor for s in base]


def uniform_matrix(n, choice):
    return [[None if i == j else choice for j in range(n)] for i in range(n)]


def best_reply_honors(others_choice, rules):
    """Your score for each number h of deals you honor, when every other decision is `others_choice`.

    Only profiles where the rest of the matrix is unanimous can trigger the -12/+15 rules;
    in every other profile the deals are independent and grabbing each one strictly pays.
    """
    n = rules.teams
    scores = []
    for h in range(n):
        m = uniform_matrix(n, others_choice)
        for j in range(1, n):
            m[0][j] = HONOR if j <= h else GRAB
        scores.append(round_scores(m, rules)[0])
    return scores


def grab_is_dominant(rules):
    """True if grabbing every deal is your unique best reply to every profile of the others."""
    if rules.grab_vs_honor <= rules.both_honor or rules.both_grab <= rules.honor_vs_grab:
        return False
    for others in (HONOR, GRAB):
        s = best_reply_honors(others, rules)
        if any(s[0] <= v for v in s[1:]):
            return False
    return True


def stage_table(rules):
    """Rows of (other teams honoring you, your score honoring all, your score grabbing all).

    The other teams honor each other; the k that honor you honor you, the rest grab you.
    """
    n = rules.teams
    rows = []
    for k in range(n):
        out = []
        for mine in (HONOR, GRAB):
            m = uniform_matrix(n, HONOR)
            for i in range(1, n):
                m[i][0] = HONOR if i <= k else GRAB
                m[0][i] = mine
            out.append(round_scores(m, rules)[0])
        rows.append((k, out[0], out[1]))
    return rows


def cooperation_threshold(rules, current_multiplier=1.0):
    """Smallest continuation probability that keeps everyone honoring every deal.

    Assumes grim-trigger punishment per deal: a team you grab grabs you for good, while the
    other teams keep honoring you. Grabbing k teams earns a one-off gain over the all-honor
    score, then costs a loss every later round; future rounds carry the expected multiplier.
    Returns (threshold, most tempting k).
    """
    n = rules.teams
    expected = 1 + rules.bonus_chance * (rules.multiplier - 1)
    worst = (0.0, None)
    for k in range(1, n):
        gain = k * rules.grab_vs_honor + (n - 1 - k) * rules.both_honor - rules.all_honor
        future = k * rules.both_grab + (n - 1 - k) * rules.both_honor
        loss = rules.all_honor - future
        if gain <= 0:
            continue
        need = 1.0 if loss <= 0 else current_multiplier * gain / (current_multiplier * gain + expected * loss)
        if need > worst[0]:
            worst = (need, k)
    return worst


# ---- Strategies -------------------------------------------------------------
# A strategy returns its decision toward one opponent. It sees: its index, the
# opponent's index, the history (list of (matrix, bonus)), whether the coming round
# is a bonus round, the round number, the rules and an RNG.

def always_honor(me, them, history, bonus, rnd, rules, rng):
    return HONOR


def always_grab(me, them, history, bonus, rnd, rules, rng):
    return GRAB


def tit_for_tat(me, them, history, bonus, rnd, rules, rng):
    """Honor a team first, then do to it what it did to you last round."""
    return history[-1][0][them][me] if history else HONOR


def grim_trigger(me, them, history, bonus, rnd, rules, rng):
    """Honor a team until it grabs you once, then grab it for good."""
    return GRAB if any(m[them][me] == GRAB for m, _ in history) else HONOR


def pavlov(me, them, history, bonus, rnd, rules, rng):
    """Win-stay, lose-shift per deal: keep last choice if that deal paid off, else switch."""
    if not history:
        return HONOR
    m = history[-1][0]
    if pair_payoff(m[me][them], m[them][me], rules) > 0:
        return m[me][them]
    return GRAB if m[me][them] == HONOR else HONOR


def bonus_grabber(me, them, history, bonus, rnd, rules, rng):
    """Tit-for-tat, but grab everyone on bonus rounds."""
    return GRAB if bonus else tit_for_tat(me, them, history, bonus, rnd, rules, rng)


def endgame_defector(me, them, history, bonus, rnd, rules, rng):
    """Tit-for-tat, but grab everyone in the final round."""
    return GRAB if rnd == rules.rounds - 1 else tit_for_tat(me, them, history, bonus, rnd, rules, rng)


def coin_flip(me, them, history, bonus, rnd, rules, rng):
    return HONOR if rng.random() < 0.5 else GRAB


STRATEGIES = {
    "Always honor": always_honor,
    "Always grab": always_grab,
    "Tit-for-tat": tit_for_tat,
    "Grim trigger": grim_trigger,
    "Pavlov": pavlov,
    "Bonus grabber": bonus_grabber,
    "Endgame defector": endgame_defector,
    "Coin flip": coin_flip,
}


@dataclass
class GameResult:
    matrices: list = field(default_factory=list)
    bonuses: list = field(default_factory=list)
    scores: list = field(default_factory=list)  # per round, per team

    def totals(self):
        return [sum(r[i] for r in self.scores) for i in range(len(self.scores[0]))] if self.scores else []


def decide(strategy_names, history, bonus, rnd, rules, rng):
    n = len(strategy_names)
    return [[None if i == j else STRATEGIES[strategy_names[i]](i, j, history, bonus, rnd, rules, rng)
             for j in range(n)] for i in range(n)]


def play(strategy_names, rules, rng, bonuses=None):
    """Play one game; `bonuses` fixes which rounds are bonus rounds (else drawn at random)."""
    if bonuses is None:
        bonuses = [rng.random() < rules.bonus_chance for _ in range(rules.rounds)]
    result = GameResult(bonuses=list(bonuses))
    history = []
    for rnd in range(rules.rounds):
        matrix = decide(strategy_names, history, bonuses[rnd], rnd, rules, rng)
        result.matrices.append(matrix)
        result.scores.append(round_scores(matrix, rules, bonuses[rnd]))
        history.append((matrix, bonuses[rnd]))
    return result


def tournament(rules, names=None, games_per_group=40, seed=7):
    """Average total score of each strategy over every group of `rules.teams` strategies."""
    names = list(names or STRATEGIES)
    rng = random.Random(seed)
    sums = {n: 0.0 for n in names}
    counts = {n: 0 for n in names}
    for group in combinations_with_replacement(names, rules.teams):
        for _ in range(games_per_group):
            totals = play(group, rules, rng).totals()
            for name, total in zip(group, totals):
                sums[name] += total
                counts[name] += 1
    return sorted(((n, sums[n] / counts[n]) for n in names), key=lambda kv: -kv[1])


if __name__ == "__main__":
    rules = Rules()
    print(f"Rules: {rules}\n")
    print("Stage game, one round, no bonus (others honor each other)")
    print(f"{'others honoring you':>20} {'you honor all':>14} {'you grab all':>13}")
    for k, h, g in stage_table(rules):
        print(f"{k:>20} {h:>14.0f} {g:>13.0f}")
    print(f"\nGrab strictly dominant: {grab_is_dominant(rules)}")
    for n in range(2, 9):
        print(f"  {n} teams: grab dominant = {grab_is_dominant(Rules(teams=n))}")
    print(f"\nNash equilibrium payoff per team per round: {rules.all_grab:.0f}")
    print(f"All-honor payoff per team per round:        {rules.all_honor:.0f}")
    for label, mult in (("normal", 1.0), ("bonus", rules.multiplier)):
        need, k = cooperation_threshold(rules, mult)
        print(f"Continuation chance needed ({label} round): {need:.3f}, most tempting: grab {k} team(s)")
    print()
    for m in (5, 20):
        print(f"Tournament, {m} rounds (average total over a game)")
        for name, score in tournament(Rules(rounds=m), games_per_group=40 if m == 5 else 10):
            print(f"  {name:<18} {score:8.2f}")

import random
from unittest import TestCase

from honor_or_grab.solver import (
    GRAB, HONOR, Rules, best_reply_honors, cooperation_threshold, grab_is_dominant, play,
    round_scores, stage_table, tournament, uniform_matrix)

H, G, _ = HONOR, GRAB, None


class TestHonorOrGrab(TestCase):
    def setUp(self):
        self.rules = Rules()

    def test_two_team_deals_match_the_rules(self):
        two = Rules(teams=2)
        self.assertEqual(round_scores([[_, G], [H, _]], two), [14, -6])
        self.assertEqual(round_scores([[_, H], [G, _]], two), [-6, 14])

    def test_unanimous_matrices_override_the_sum(self):
        self.assertEqual(round_scores(uniform_matrix(4, G), self.rules), [-12] * 4)
        self.assertEqual(round_scores(uniform_matrix(4, H), self.rules), [15] * 4)

    def test_each_pair_settles_its_own_deal(self):
        # Team 0 grabs team 1 only; everyone else honors everyone.
        m = uniform_matrix(4, H)
        m[0][1] = G
        self.assertEqual(round_scores(m, self.rules), [14 + 6 + 6, -6 + 6 + 6, 18, 18])

    def test_decisions_toward_different_teams_can_differ(self):
        # Team 0 honors 1, grabs 2; team 1 grabs 0; team 2 honors 0; 1 and 2 grab each other.
        m = [[_, H, G], [G, _, G], [H, G, _]]
        self.assertEqual(round_scores(m, Rules(teams=3)), [-6 + 14, 14 - 4, -6 - 4])

    def test_bonus_round_multiplies_every_score(self):
        m = uniform_matrix(4, H)
        m[0][1] = G
        self.assertEqual(round_scores(m, self.rules, bonus=True), [78, 18, 54, 54])

    def test_stage_table(self):
        self.assertEqual(stage_table(self.rules), [(0, -18, -12), (1, -6, 6), (2, 6, 24), (3, 15, 42)])

    def test_grab_is_strictly_dominant_from_four_teams(self):
        for n in range(4, 9):
            self.assertTrue(grab_is_dominant(Rules(teams=n)))

    def test_small_groups_break_the_dilemma(self):
        # Two teams: honor beats grab whatever the rival does (15 > 14, -6 > -12).
        self.assertEqual(best_reply_honors(H, Rules(teams=2)), [14, 15])
        self.assertEqual(best_reply_honors(G, Rules(teams=2)), [-12, -6])
        self.assertFalse(grab_is_dominant(Rules(teams=2)))
        # Three teams: against two total grabbers, honoring exactly one deal (-10) beats -12.
        self.assertEqual(best_reply_honors(G, Rules(teams=3)), [-12, -10, -12])
        self.assertFalse(grab_is_dominant(Rules(teams=3)))

    def test_tit_for_tat_mirrors_each_team_separately(self):
        rng = random.Random(0)
        result = play(["Tit-for-tat", "Always grab", "Always honor", "Always honor"], self.rules, rng,
                      bonuses=[False] * 5)
        first, second = result.matrices[0][0], result.matrices[1][0]
        self.assertEqual(first[1:], [H, H, H])
        self.assertEqual(second[1:], [G, H, H])

    def test_grim_trigger_only_punishes_the_offender(self):
        rng = random.Random(0)
        result = play(["Grim trigger", "Bonus grabber", "Always honor", "Always honor"], self.rules, rng,
                      bonuses=[False, True, False, False, False])
        self.assertEqual([m[0][1] for m in result.matrices], [H, H, G, G, G])
        self.assertEqual([m[0][2] for m in result.matrices], [H] * 5)

    def test_endgame_defector_grabs_everyone_last_round(self):
        rng = random.Random(0)
        result = play(["Endgame defector"] + ["Always honor"] * 3, self.rules, rng, bonuses=[False] * 5)
        self.assertEqual(result.matrices[-1][0][1:], [G, G, G])
        self.assertEqual(result.matrices[-2][0][1:], [H, H, H])

    def test_cooperation_threshold_driven_by_grabbing_one_team(self):
        # Grab one of three honorers: gain 14 + 6 + 6 - 15 = 11, then lose 15 - (6 + 6 - 4) = 7 a round.
        need, k = cooperation_threshold(self.rules)
        self.assertEqual(k, 1)
        self.assertAlmostEqual(need, 11 / (11 + 1.5 * 7))
        need_bonus, _ = cooperation_threshold(self.rules, current_multiplier=3)
        self.assertAlmostEqual(need_bonus, 33 / (33 + 1.5 * 7))

    def test_reciprocators_beat_always_grab(self):
        ranking = [name for name, _ in tournament(self.rules, games_per_group=5, seed=3)]
        self.assertEqual(ranking[-1], "Always grab")
        self.assertLess(ranking.index("Tit-for-tat"), ranking.index("Always grab"))

    def test_tournament_is_reproducible(self):
        a = tournament(Rules(rounds=3), games_per_group=3, seed=11)
        b = tournament(Rules(rounds=3), games_per_group=3, seed=11)
        self.assertEqual(a, b)

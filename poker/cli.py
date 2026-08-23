from poker.hand_evaluator import HandEvaluator
from poker.player import HumanPlayer, MachinePlayer
from poker.strategy import MonteCarloStrategy
from poker.table import BettingRound, Table


def _run_betting_round(table: Table) -> None:
    if len(table.active_players()) <= 1:
        return
    table.start_betting_round()
    while not table.is_betting_round_complete():
        actor = table.current_actor()
        if actor is None:
            break
        action, amount = actor.act(table)
        table.apply_action(actor, action, amount)
    pass


def play_hand(table: Table) -> None:
    table.start_hand()
    table.deal_hole_cards()
    table.post_blinds()
    _run_betting_round(table)

    for deal_next in (table.deal_flop, table.deal_turn, table.deal_river):
        if len(table.active_players()) <= 1:
            break
        deal_next()
        _run_betting_round(table)

    live = table.active_players()
    if len(live) == 1:
        winner = live[0]
        winner.stack += table.pot
        print('%s wins the pot of %d (everyone else folded)' % (winner.name, table.pot))
    else:
        table.current_round = BettingRound.SHOWDOWN
        ranked = [(HandEvaluator.evaluate(player.hole_cards + table.community_cards), player)
                  for player in live]
        best_rank = max(rank for rank, _ in ranked)
        winners = [player for rank, player in ranked if rank == best_rank]
        share = table.pot // len(winners)
        for winner in winners:
            winner.stack += share
        print('showdown: board=%s' % [str(card) for card in table.community_cards])
        for rank, player in ranked:
            print('  %s: %s -> %s' % (
                player.name, [str(card) for card in player.hole_cards], rank.category.name))
        print('winner(s): %s split pot of %d' % ([w.name for w in winners], table.pot))

    table.pot = 0
    table.button_index = (table.button_index + 1) % len(table.players)
    pass


def remove_busted_players(table: Table) -> None:
    table.players = [player for player in table.players if player.stack > 0]
    if table.players:
        table.button_index = table.button_index % len(table.players)
    pass


if __name__ == '__main__':
    human = HumanPlayer('You', 200)
    bots = [MachinePlayer('Bot%d' % i, 200, MonteCarloStrategy(num_simulations=300))
            for i in range(1, 3)]
    table = Table([human] + bots, small_blind=1, big_blind=2)

    while human.stack > 0 and len([p for p in table.players if p.stack > 0]) > 1:
        play_hand(table)
        remove_busted_players(table)
        print('stacks: %s' % {p.name: p.stack for p in table.players})
        if input('play another hand? (y/n): ').strip().lower() != 'y':
            break
    pass

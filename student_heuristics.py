"""
Evaluation functions implemented
"""

import time
from sample_players import improved_score

def density(game, player):
    """
    return an indication of density around the player

    We just look at the
    :param game:
    :param player:
    :return:
    """
    def is_in_board(x, y, game):
        return (0 <= x < game.width) and (0 <= y < game.height)

    player_location = game.get_player_location(player)
    cells = [(player_location[0]+i, player_location[1]+j) for i in [-2, -1, 0, 1, 2] for j in [-2, -1, 0, 1, 2]]
    cells_arround = [cell for cell in cells if is_in_board(cell[0], cell[1], game)]
    free_cells_arround = [cell for cell in cells_arround if (game.__board_state__[cell[0]][cell[1]] == game.BLANK)]
    max_free_cell = 24
    return len(free_cells_arround) / max_free_cell


def diff_density(game, player):
    return density(game, player) - density(game, game.get_opponent(player))


def combined_improved_and_density(game, player):
    return improved_score(game, player) + diff_density(game, player)


def combined_improved_density_at_end(game, player):
    """
    Simple evaluation function that combine improved-score heuristic and density function heuristic
    """
    if game.move_count < 20:
        # At the beginning we need to go fast
        score = improved_score(game, player)
    else:
        # At the end of a game/middle of a game we need a more precise heuristic that could take a bit more of time
        score = improved_score(game, player) + diff_density(game, player)
    return float(score)


def combined_full(game, player):
    if game.move_count < 10:
        return distance_to_center(game, player)
    if game.move_count < 20:
        return improved_score(game, player)
    # if above 20:
    return improved_score(game, player) + diff_density(game, player)


def agrressive_first_then_preserving(game, player):
    """
    fonctionne pas trop mal
    :param game:
    :param player:
    :return:
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    total_space = game.width * game.height
    game_duration = len(game.get_blank_spaces()) / float(total_space)

    if game_duration <= 0.25:
        # aggressif en debut de partie..
        return improved_agressive(game, player)
    else:
        return improved_score(game, player)


def improved_with_sleep(game, player):
    """
    return opposite of improved_score, so we help the opponnent
    :param game:
    :param player:
    :return:
    """
    res = -improved_score(game, player)
    time.sleep(0.01)  # just to make sure we timeout a lot
    return float(res)


def custom_score_knight_tour(game, player):
    """
    We use the Warnsdorf's rule so we go first to cell with fewest onward moves (if it's more than 1)
    :param game:
    :param player:
    :return:
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    nb_moves = len(game.get_legal_moves(player=player))
    score = 8 - nb_moves
    return float(score)


def improved_agressive(game, player):

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(game.active_player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))

    return float(own_moves - 2 * opp_moves)


def improved_preserving(game, player):

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(game.active_player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))

    return float(2 * own_moves - opp_moves)


def distance_to_center(game, player):
    def distance(pos, target):
        res = abs(pos[0] - target[0]) + abs(pos[1] - target[1])
        return res

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    distance_to_center = distance(game.get_player_location(player), (game.width//2.0, game.height//2.0))

    return distance_to_center



"""
Simple web api so we can play against the IA in a web browser
"""

import falcon
from game_agent import CustomPlayer, custom_score_knight_tour
from isolation import Board
import json
import timeit
from falcon_cors import CORS

TIME_LIMIT_MILLIS = 200

class WrongPlayer(Exception):
    pass

class InvalidMove(Exception):
    pass

class Game:
    def __init__(self):
        self.human_player = None  # it's the human player
        self.ia_player = CustomPlayer(method='alphabeta', iterative=False, score_fn=custom_score_knight_tour)
        self.board = Board(self.human_player, self.ia_player)

    def do_human_move(self, move):
        if self.board.active_player != self.human_player:
            raise WrongPlayer

        legal_player_moves = self.board.get_legal_moves(self.board.active_player)
        if not(move in legal_player_moves):
            raise InvalidMove("{} not found in {}".format(move, legal_player_moves))

        self.board.apply_move(move)

    def do_ia_move(self, time_limit=TIME_LIMIT_MILLIS):
        if self.board.active_player != self.ia_player:
            raise WrongPlayer

        legal_player_moves = self.board.get_legal_moves(self.board.active_player)

        curr_time_millis = lambda: 1000 * timeit.default_timer()
        move_start = curr_time_millis()
        time_left = lambda : time_limit - (curr_time_millis() - move_start)
        game_copy = self.board.copy()
        curr_move = self.board.active_player.get_move(game_copy, legal_player_moves, time_left)
        move_end = time_left()
        self.board.apply_move(curr_move)
        return curr_move

    def display_board(self):
        print(self.board.to_string())


class GameInfoRessource(object):
    def on_get(self, req, resp):
        resp_dict = {'width': game.board.width, 'height': game.board.height, 'player1_name': "human", 'player2_name': "IA"}
        resp.body = json.dumps(resp_dict, ensure_ascii=False)
        print("Get info ressource res is {}".format(resp.body))

class HumanPossibleMove(object):
    def on_get(self, req, resp):
        legal_moves = game.board.get_legal_moves(game.human_player)
        print("legal moves are {}".format(legal_moves))
        resp.body = json.dumps(legal_moves, ensure_ascii=False)

class HumanMove(object):
    def on_post(self, req, resp):
        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest(
                'Empty request body',
                'A valid JSON document is required.'
            )

        try:
            print("trying to parse json {}".format(body.decode('utf-8')))
            req.context["req_body"] = json.loads(body.decode('utf-8'))
            # don't do that in standard output for indus version
            print("Received:")
            print(json.dumps(req.context['req_body']))
        except Exception as e:
            print("exception {} oocurs".format(e))
            raise(e)

        move  = int(req.context["req_body"]['move_coord'][0]), int(req.context["req_body"]['move_coord'][1])
        print(move)

        try:
            game.do_human_move(move)
            game.display_board()
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(move, ensure_ascii=False)
        except Exception as e:
            resp.data = str(e)
            resp.status = falcon.HTTP_400

class IANextMove(object):
    def on_get(self, req, resp):
        print("Get with {} and resp {}".format(req, resp))
        next_move = game.do_ia_move()
        print("next ia moves is {}".format(next_move))
        resp.body = json.dumps(next_move, ensure_ascii=False)
        print(game.display_board())


ALLOWED_ORIGINS = ['http://localhost:8000'] # Or load this from a config file


cors = CORS(allow_methods_list=['POST', 'GET'], allow_origins_list=['http://127.0.0.1:8001'],  allow_credentials_all_origins=True, allow_all_headers=True)
game = Game()
api = falcon.API(middleware=[cors.middleware])
api.add_route("/v1/game_info", GameInfoRessource())
api.add_route("/v1/ia/next_move", IANextMove())
api.add_route("/v1/human/legal_moves", HumanPossibleMove())
api.add_route("/v1/human/move", HumanMove())

#g = Game()

from wsgiref import simple_server

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()
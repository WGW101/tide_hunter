import math
import random
import collections
import itertools


WEATHER_CARDS = list(range(1, 61))
TIDE_CARDS = list(range(1, 13)) * 2


def n_buoys(card):
    if card < 13 or card > 48:
        return 0
    elif card < 25 or card > 36:
        return 0.5
    else:
        return 1


def count_buoys(cards):
    return math.floor(sum(n_buoys(card) for card in cards))


class Player:
    count = itertools.count()
    def __init__(self, game, name=None):
        self.game = game
        self.name = "Player {}".format(next(Player.count)) if name is None else name
        self.score = 0

    def start_round(self, hand, buoys):
        self.hand = hand.copy()
        self.buoys = buoys
        self.tide = 0
        self.played_cards = []

    def play_chosen_card(self):
        self.hand.remove(self.chosen_card)
        self.played_cards.append(self.chosen_card)
        self.chosen_card = None

    def choose_card(self):
        raise NotImplementedError()


class DummyPlayer(Player):
    def choose_card(self):
        self.chosen_card = random.choice(self.hand)


class HumanPlayer(Player):
    def choose_card(self):
        for player in self.game.players:
            if player == self:
                print("YOU:", end=" ")
            else:
                print("    ", end=" ")
            print(repr(player.name), player.buoys, player.tide, player.played_cards)
        print("Tides on board:", self.game.tides_on_board)
        print("Your hand:", self.hand)
        while True:
            try:
                self.chosen_card = int(input("> "))
                if self.chosen_card in self.hand:
                    break
            except ValueError:
                pass
            print("Invalid input, please retry.")


class Game:
    def __init__(self, n_players=5):
        self.n_players = n_players
        random.shuffle(WEATHER_CARDS)
        self.init_hands = collections.deque(sorted(WEATHER_CARDS[12*i:12*(i+1)]) for i in range(n_players))
        self.init_buoys = collections.deque(count_buoys(hand) for hand in self.init_hands)
        self.players = [HumanPlayer(self) for i in range(n_players)]

    def start_round(self, r):
        self.round_tides = TIDE_CARDS.copy()
        random.shuffle(self.round_tides)
        for player, hand, buoys in zip(self.players, self.init_hands, self.init_buoys):
            player.start_round(hand, buoys)
        self.active_players = self.players.copy()

    def end_round(self):
        for player in self.players:
            player.score += player.buoys()
        min_tide_player = min(self.active_players, key=lambda player: player.tide)
        min_tide_player.score += 1
        self.init_hands.rotate()
        self.init_buoys.rotate()

    def play_turn(self, t):
        self.tides_on_board = sorted(self.round_tides[2*t:2*(t+1)])

        for player in self.active_players:
            player.choose_card()
        sorted_players = sorted(self.active_players, key=lambda player: player.chosen_card, reverse=True)
        for player in self.active_players:
            player.play_chosen_card()

        for player, tide in zip(sorted_players, self.tides_on_board):
            player.tide = tide
        sorted_players = sorted(self.active_players, key=lambda player: player.tide, reverse=True)
        for tide, players in itertools.groupby(sorted_players, key=lambda player: player.tide):
            for player in players:
                player.buoys -= 1
                if player.buoys < 0:
                    self.active_players.remove(player)
                    another_loose = True
                else:
                    another_loose = False
            if not another_loose:
                break

    def end_game(self):
        scoreboard = sorted(self.players, key=lambda player: player.score, reverse=True)
        print("=== Scoreboard ===")
        print('\n'.join(
            "{}. {} ({})".format(i, player.name, player.score)
            for i, player in enumerate(scoreboard, start=1)))

    def run(self):
        for r in range(self.n_players):
            self.start_round(r)
            for t in range(12):
                self.play_turn(t)
            self.end_round()
        self.end_game()


if __name__ == "__main__":
    game = Game(3)
    game.run()

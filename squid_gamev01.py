# squid_game v0.1.0
# elapsed time

import random
import time

class Player:
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed
        self.position = 0
        self.is_out = False

class RedLightGreenLight:
    def __init__(self, players, field_length=100, time_limit=100):
        self.players = players
        self.field_length = field_length
        self.time_limit = time_limit
        self.red_light = False
        self.total_players = len(players)
        self.remaining_players = self.total_players
        self.elapsed_time = 0

    def start_game(self):
        while not self.check_winner() and self.remaining_players > 0 and self.elapsed_time < self.time_limit:
            self.red_light = random.choice([True, False])
            print("Red Light!" if self.red_light else "Green Light!")
            self.update_positions()
            self.check_eliminations()
            time.sleep(0.1)  # simulation step
            self.elapsed_time += 1
            self.report_status()

        self.check_time_limit()
        self.report_final()

    def update_positions(self):
        if not self.red_light:
            for player in self.players:
                if not player.is_out:
                    player.position += player.speed

    def check_eliminations(self):
        if self.red_light:
            for player in self.players:
                if not player.is_out and player.position > 0 and random.random() < 0.1:
                    player.is_out = True
                    self.remaining_players -= 1

    def check_winner(self):
        for player in self.players:
            if player.position >= self.field_length:
                return True
        return False

    def check_time_limit(self):
        if self.elapsed_time >= self.time_limit:
            for player in self.players:
                if not player.is_out and player.position < self.field_length:
                    player.is_out = True
                    self.remaining_players -= 1

    def report_status(self):
        print(f"Remaining Players: {self.remaining_players}/{self.total_players}. Elapsed Time: {self.elapsed_time:.1f}s")

    def report_final(self):
        survivors = len([p for p in self.players if not p.is_out])
        print(f"Game Over. Survivors: {survivors}/{self.total_players} ({survivors/self.total_players*100:.2f}%)")

# Creating 456 players with random speeds between 1 and 10
players = [Player(f"Player {i+1}", random.randint(1, 10)) for i in range(456)]
game = RedLightGreenLight(players, time_limit=300)  # Set a time limit of 300 seconds (5 minutes)
game.start_game()

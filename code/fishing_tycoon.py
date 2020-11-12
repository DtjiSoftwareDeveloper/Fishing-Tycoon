"""
This file contains code for the game "Fishing Tycoon".
Author: DtjiSoftwareDeveloper
"""

# Importing necessary libraries

import sys
import uuid
import pickle
import copy
import random
from datetime import datetime
import os
from mpmath import *

mp.pretty = True


# Creating static functions to be used throughout the game


def is_number(string: str) -> bool:
    try:
        mpf(string)
        return True
    except ValueError:
        return False


def triangular(n: int) -> int:
    return int(n * (n - 1) / 2)


def mpf_sum_of_list(a_list: list) -> mpf:
    return mpf(str(sum(mpf(str(elem)) for elem in a_list if is_number(str(elem)))))


def load_game_data(file_name):
    # type: (str) -> Game
    return pickle.load(open(file_name, "rb"))


def save_game_data(game_data, file_name):
    # type: (Game, str) -> None
    pickle.dump(game_data, open(file_name, "wb"))


def clear():
    # type: () -> None
    if sys.platform.startswith('win'):
        os.system('cls')  # For Windows System
    else:
        os.system('clear')  # For Linux System


# Creating necessary classes


class Player:
    """
    This class contains attributes of the player in this game.
    """

    def __init__(self, name):
        # type: (str) -> None
        self.player_id: str = str(uuid.uuid1())  # Generates random player ID
        self.name: str = name
        self.level: int = 1
        self.attack_power: mpf = mpf("500")
        self.fishing_rod: FishingRod or None = None
        self.__fishing_rods_owned: list = []  # initial value
        self.aquarium: Aquarium = Aquarium()
        self.exp: mpf = mpf("0")
        self.required_exp: mpf = mpf("1e6")
        self.coins: mpf = mpf("0")

    def __str__(self):
        # type: () -> str
        res: str = ""  # initial value
        res += "Player ID: " + str(self.player_id) + "\n"
        res += "Name: " + str(self.name) + "\n"
        res += "Level: " + str(self.level) + "\n"
        res += "EXP: " + str(self.exp) + "\n"
        res += "Required EXP to reach next level: " + str(self.required_exp) + "\n"
        res += "Coins: " + str(self.coins) + "\n"
        res += "Attack Power: " + str(self.attack_power) + "\n"
        res += "Fishing Rod used:\n" + str(self.fishing_rod) + "\n"
        res += "Below is a list of fishing rods owned by this player.\n"
        for rod in self.__fishing_rods_owned:
            res += str(rod) + "\n"

        res += "Below is a list of sea creatures in this player's aquarium:\n"
        for sea_creature in self.aquarium.get_sea_creatures():
            res += str(sea_creature) + "\n"

        return res

    def level_up_fishing_rod(self):
        # type: () -> bool
        if isinstance(self.fishing_rod, FishingRod):
            if self.coins >= self.fishing_rod.level_up_coin_cost:
                self.coins -= self.fishing_rod.level_up_coin_cost
                self.fishing_rod.level_up()
                return True
            return False
        return False

    def gain_exp_after_time(self, seconds):
        # type: (int) -> None
        total_exp_gained: mpf = \
            mpf_sum_of_list([sea_creature.exp_per_second for sea_creature in self.aquarium.get_sea_creatures()]) \
            * seconds
        self.exp += total_exp_gained
        self.level_up()

    def gain_coins_after_time(self, seconds):
        # type: (int) -> None
        total_coins_gained: mpf = \
            mpf_sum_of_list([sea_creature.coins_per_second for sea_creature in self.aquarium.get_sea_creatures()]) \
            * seconds
        self.coins += total_coins_gained

    def catch_sea_creature(self, sea_creature):
        # type: (SeaCreature) -> bool
        if sea_creature.curr_hp <= 0:
            self.aquarium.add_sea_creature(sea_creature)
            self.exp += sea_creature.catch_exp_reward
            self.level_up()
            return True
        return False

    def add_fishing_rod(self, fishing_rod):
        # type: (FishingRod) -> None
        if self.fishing_rod is not None:
            curr_fishing_rod: FishingRod = self.fishing_rod
            self.attack_power += fishing_rod.attack_power - curr_fishing_rod.attack_power
            self.fishing_rod = fishing_rod
        else:
            self.attack_power += fishing_rod.attack_power
            self.fishing_rod = fishing_rod

    def remove_fishing_rod(self):
        # type: () -> bool
        if self.fishing_rod is not None:
            curr_fishing_rod: FishingRod = self.fishing_rod
            self.attack_power -= curr_fishing_rod.attack_power
            self.fishing_rod = None
            return True
        else:
            return False

    def buy_fishing_rod(self, fishing_rod):
        # type: (FishingRod) -> bool
        if self.coins >= fishing_rod.coin_cost:
            self.coins -= fishing_rod.coin_cost
            self.__fishing_rods_owned.append(fishing_rod)
            return True
        return False

    def sell_fishing_rod(self, fishing_rod):
        # type: (FishingRod) -> bool
        if fishing_rod in self.__fishing_rods_owned:
            self.__fishing_rods_owned.remove(fishing_rod)
            self.coins += fishing_rod.coin_cost
            return True
        return False

    def get_fishing_rods_owned(self):
        # type: () -> list
        return self.__fishing_rods_owned

    def level_up(self):
        # type: () -> None
        while self.exp >= self.required_exp:
            self.level += 1
            self.required_exp *= mpf("10") ** self.level
            self.attack_power *= triangular(self.level)

    def clone(self):
        # type: () -> Player
        return copy.deepcopy(self)


class Aquarium:
    """
    This class contains attributes of player's aquarium.
    """

    def __init__(self, sea_creatures=None):
        # type: (list) -> None
        if sea_creatures is None:
            sea_creatures = []
        self.__sea_creatures: list = sea_creatures  # initial value

    def get_sea_creatures(self):
        # type: () -> list
        return self.__sea_creatures

    def add_sea_creature(self, sea_creature):
        # type: (SeaCreature) -> None
        self.__sea_creatures.append(sea_creature)

    def clone(self):
        # type: () -> Aquarium
        return copy.deepcopy(self)


class SeaCreature:
    """
    This class contains attributes of a sea creature
    """

    def __init__(self, name, max_hp, catch_exp_reward, exp_per_second, coins_per_second, flee_chance):
        # type: (str, mpf, mpf, mpf, mpf, float) -> None
        self.name: str = name
        self.curr_hp: mpf = max_hp
        self.max_hp: mpf = max_hp
        self.catch_exp_reward: mpf = catch_exp_reward
        self.exp_per_second: mpf = exp_per_second
        self.coins_per_second: mpf = coins_per_second
        self.flee_chance: float = flee_chance

    def __str__(self):
        # type: () -> str
        res: str = ""  # initial value
        res += "Name: " + str(self.name) + "\n"
        res += "EXP Reward for catching this sea creature: " + str(self.catch_exp_reward) + "\n"
        res += "HP: " + str(self.curr_hp) + "/" + str(self.max_hp) + "\n"
        res += "EXP per second: " + str(self.exp_per_second) + "\n"
        res += "Coins per second: " + str(self.coins_per_second) + "\n"
        res += "Flee chance: " + str(self.flee_chance * 100) + "%\n"
        return res

    def clone(self):
        # type: () -> SeaCreature
        return copy.deepcopy(self)


class FishingRod:
    """
    This class contains attributes of a fishing rod.
    """

    def __init__(self, name, attack_power, coin_cost):
        # type: (str, mpf, mpf) -> None
        self.name: str = name
        self.level: int = 1
        self.attack_power: mpf = attack_power
        self.critical_damage: mpf = mpf("1.5")
        self.coin_cost: mpf = coin_cost
        self.level_up_coin_cost: mpf = coin_cost

    def level_up(self):
        # type: () -> None
        self.level += 1
        self.attack_power *= mpf("10") ** self.level
        self.critical_damage += mpf("0.1") * self.level
        self.level_up_coin_cost *= mpf("10") ** self.level

    def __str__(self):
        # type: () -> str
        res: str = ""  # initial value
        res += "Name: " + str(self.name) + "\n"
        res += "Attack Power: " + str(self.attack_power) + "\n"
        res += "Critical Damage: " + str(self.critical_damage * 100) + "%\n"
        res += "Purchase Coin Cost: " + str(self.coin_cost) + "\n"
        res += "Level Up Coin Cost: " + str(self.level_up_coin_cost) + "\n"
        return res

    def clone(self):
        # type: () -> FishingRod
        return copy.deepcopy(self)


class BodyOfWater:
    """
    This class contains attributes of a body of water.
    """

    def __init__(self, name, minimum_player_level, potential_sea_creatures):
        # type: (str, int, list) -> None
        self.name: str = name
        self.minimum_player_level: int = minimum_player_level
        self.__potential_sea_creatures: list = potential_sea_creatures

    def __str__(self):
        # type: () -> str
        res: str = ""  # initial value
        res += "Name: " + str(self.name) + "\n"
        res += "Minimum Player Level to fish here: " + str(self.minimum_player_level) + "\n"
        res += "Below is a list of sea creatures which can be caught here:\n"
        for sea_creature in self.__potential_sea_creatures:
            res += str(sea_creature) + "\n"

        return res

    def get_potential_sea_creatures(self):
        # type: () -> list
        return self.__potential_sea_creatures

    def clone(self):
        # type: () -> BodyOfWater
        return copy.deepcopy(self)


class Shop:
    """
    This class contains attributes of a shop to buy fishing rods.
    """

    def __init__(self, name, fishing_rods_sold):
        # type: (str, list) -> None
        self.name: str = name
        self.__fishing_rods_sold: list = fishing_rods_sold

    def get_fishing_rods_sold(self):
        # type: () -> list
        return self.__fishing_rods_sold

    def clone(self):
        # type: () -> Shop
        return copy.deepcopy(self)


class Game:
    """
    This class contains attributes of saved game data.
    """

    def __init__(self, player, bodies_of_water, shop):
        # type: (Player, list, Shop) -> None
        self.player: Player = player
        self.__bodies_of_water: list = bodies_of_water
        self.shop: Shop = shop

    def get_bodies_of_water(self):
        # type: () -> list
        return self.__bodies_of_water

    def clone(self):
        # type: () -> Game
        return copy.deepcopy(self)


# Creating main function used to run the game.


def main():
    """
    This main function is used to run the game.
    :return: None
    """

    print("Welcome to 'Fishing Tycoon' by 'DtjiSoftwareDeveloper'.")
    print("In this game, you will go fishing to catch sea creatures.")

    sea_creatures: list = [
        SeaCreature("Pegaklesk", mpf("1e4"), mpf("2e3"), mpf("1e3"), mpf("1e3"), 0),
        SeaCreature("Sunup", mpf("1e5"), mpf("2e4"), mpf("1e4"), mpf("1e4"), 0.05),
        SeaCreature("Siledraor", mpf("1e7"), mpf("2e6"), mpf("1e6"), mpf("1e6"), 0.1),
        SeaCreature("Rutind", mpf("1e10"), mpf("2e9"), mpf("1e9"), mpf("1e9"), 0.15),
        SeaCreature("Sirto", mpf("1e14"), mpf("2e13"), mpf("1e13"), mpf("1e13"), 0.2),
        SeaCreature("Thotorog", mpf("1e19"), mpf("2e18"), mpf("1e18"), mpf("1e18"), 0.25),
        SeaCreature("Erok", mpf("1e25"), mpf("2e24"), mpf("1e24"), mpf("1e24"), 0.3),
        SeaCreature("Aket", mpf("1e32"), mpf("2e31"), mpf("1e31"), mpf("1e31"), 0.35),
        SeaCreature("Tunaba", mpf("1e40"), mpf("2e39"), mpf("1e39"), mpf("1e39"), 0.4),
        SeaCreature("Keoyhu", mpf("1e49"), mpf("2e48"), mpf("1e48"), mpf("1e48"), 0.45)
    ]

    bodies_of_water: list = [
        BodyOfWater("Hampswell Gulf", 1, sea_creatures[0:5]),
        BodyOfWater("Beauford Waters", 5, sea_creatures[5::])
    ]

    shop: Shop = Shop(
        "Fishing Rod Shop",
        [
            FishingRod("Fishing Rod #1", mpf("1e3"), mpf("1e5")),
            FishingRod("Fishing Rod #2", mpf("1e5"), mpf("1e8")),
            FishingRod("Fishing Rod #3", mpf("1e8"), mpf("1e12")),
            FishingRod("Fishing Rod #4", mpf("1e12"), mpf("1e17")),
            FishingRod("Fishing Rod #5", mpf("1e17"), mpf("1e23")),
            FishingRod("Fishing Rod #6", mpf("1e23"), mpf("1e30")),
            FishingRod("Fishing Rod #7", mpf("1e30"), mpf("1e38")),
            FishingRod("Fishing Rod #8", mpf("1e38"), mpf("1e47")),
            FishingRod("Fishing Rod #9", mpf("1e47"), mpf("1e57")),
            FishingRod("Fishing Rod #10", mpf("1e57"), mpf("1e68"))
        ])

    # Automatically load saved game data
    file_name: str = "SAVED FISHING TYCOON GAME DATA"
    new_game: Game
    try:
        new_game = load_game_data(file_name)
        print("Current game progress:\n", str(new_game))
    except FileNotFoundError:
        name: str = input("Please enter your name: ")
        player: Player = Player(name)
        new_game = Game(player, bodies_of_water, shop)

    old_now = datetime.now()
    print("Enter 'Y' for yes.")
    print("Enter anything else for no.")
    continue_playing: str = input("Do you want to continue playing 'Fishing Tycoon'? ")
    while continue_playing == "Y":
        # Clearing up the command line window
        clear()

        # Updating the old now time and granting EXP and coins to the player
        new_now = datetime.now()
        time_difference = new_now - old_now
        seconds: int = time_difference.seconds
        old_now = new_now
        new_game.player.gain_coins_after_time(seconds)
        new_game.player.gain_exp_after_time(seconds)

        # Asking the player what he/she wants to do inside the game.
        allowed: list = ["GO FISHING", "GO SHOPPING", "UPGRADE FISHING ROD", "SELL FISHING ROD", "EQUIP FISHING ROD",
                         "UNEQUIP FISHING ROD", "VIEW STATS"]
        print("Enter 'GO FISHING' to go fishing.")
        print("Enter 'GO SHOPPING' to go shopping.")
        print("Enter 'UPGRADE FISHING ROD' to upgrade a fishing rod.")
        print("Enter 'SELL FISHING ROD' to sell a fishing rod.")
        print("Enter 'EQUIP FISHING ROD' to equip fishing rod.")
        print("Enter 'UNEQUIP FISHING ROD' to unequip fishing rod.")
        print("Enter 'VIEW STATS' to view your stats.")
        print("Enter anything else to save game data and quit the game.")
        action: str = input("What do you want to do? ")
        if action not in allowed:
            # Saving game data and quitting the game
            save_game_data(new_game, file_name)
            sys.exit()
        else:
            if action == "GO FISHING":
                # Clearing up the command line window
                clear()

                print("Below is a list of bodies of water where you can go fishing.\n")
                for body_of_water in new_game.get_bodies_of_water():
                    print(str(body_of_water) + "\n")

                body_of_water_index: int = int(input("Please enter index of body of water you want to go to: "))
                while body_of_water_index < 0 or body_of_water_index >= len(new_game.get_bodies_of_water()) or \
                    (0 <= body_of_water_index < len(new_game.get_bodies_of_water()) and
                     new_game.get_bodies_of_water()[body_of_water_index].minimum_player_level > new_game.player.level):
                    body_of_water_index = int(input("Sorry, invalid input! "
                                                    "Please enter index of body of water you want to go to: "))

                selected_body_of_water: BodyOfWater = new_game.get_bodies_of_water()[body_of_water_index]
                wild_sea_creature: SeaCreature = selected_body_of_water.get_potential_sea_creatures()[random.randint
                (0, len(selected_body_of_water.get_potential_sea_creatures()) - 1)]
                print("A wild " + str(wild_sea_creature.name) + " appeared!")
                print("Enter 'Y' for yes.")
                print("Enter anything else for no.")
                catch: str = input("Do you want to catch " + str(wild_sea_creature.name) + "? ")
                if catch == "Y":
                    sea_creature_flees: bool = False  # initial value
                    while wild_sea_creature.curr_hp > 0 and not sea_creature_flees:
                        # Asking the player whether he/she wants to attack the sea creature or flee
                        print("Enter 'ATTACK' to attack.")
                        print("Enter anything else to flee.")
                        action: str = input("What do you want to do with the sea creature? ")
                        if action == "ATTACK":
                            has_fishing_rod: bool = new_game.player.fishing_rod is not None
                            if has_fishing_rod:
                                is_crit: bool = random.random() <= 0.3
                                damage: mpf = new_game.player.attack_power if not is_crit else \
                                    new_game.player.attack_power * new_game.player.fishing_rod.critical_damage
                                wild_sea_creature.curr_hp -= damage
                            else:
                                wild_sea_creature.curr_hp -= new_game.player.attack_power

                            sea_creature_flees = random.random() <= wild_sea_creature.flee_chance
                        else:
                            break

                    if wild_sea_creature.curr_hp <= 0:
                        print("You have successfully caught " + str(wild_sea_creature.name) + "!")
                        new_game.player.catch_sea_creature(wild_sea_creature)

            elif action == "GO SHOPPING":
                # Clearing up the command line window
                clear()

                print("Below is a list of fishing rods sold in " + str(new_game.shop.name) + ".\n")
                for fishing_rod in new_game.shop.get_fishing_rods_sold():
                    print(str(fishing_rod) + "\n")

                fishing_rod_index: int = int(input("Please enter index of fishing rod you want to buy: "))
                while fishing_rod_index < 0 or fishing_rod_index >= len(new_game.shop.get_fishing_rods_sold()):
                    fishing_rod_index = int(input("Sorry, invalid input! "
                                                  "Please enter index of fishing rod you want to buy: "))

                to_buy: FishingRod = new_game.shop.get_fishing_rods_sold()[fishing_rod_index]
                new_game.player.buy_fishing_rod(to_buy)

            elif action == "UPGRADE FISHING ROD":
                # Clearing up the command line window
                clear()

                if isinstance(new_game.player.fishing_rod, FishingRod):
                    if new_game.player.coins >= new_game.player.fishing_rod.level_up_coin_cost:
                        new_game.player.fishing_rod.level_up()
                    else:
                        print("Sorry, you have insufficient coins!")
                else:
                    pass  # Do nothing

            elif action == "SELL FISHING ROD":
                # Clearing up the command line window
                clear()

                if len(new_game.player.get_fishing_rods_owned()) == 0:
                    pass  # Do nothing
                else:
                    print("Below is a list of fishing rods you have:\n")
                    for fishing_rod in new_game.player.get_fishing_rods_owned():
                        print(str(fishing_rod) + "\n")

                    fishing_rod_index: int = int(input("Please enter index of fishing rod you want to sell: "))
                    while fishing_rod_index < 0 or fishing_rod_index >= len(new_game.player.get_fishing_rods_owned()):
                        fishing_rod_index = int(input("Sorry, invalid input! "
                                                      "Please enter index of fishing rod you want to sell: "))

                    to_sell: FishingRod = new_game.player.get_fishing_rods_owned()[fishing_rod_index]
                    new_game.player.sell_fishing_rod(to_sell)

            elif action == "EQUIP FISHING ROD":
                # Clearing up the command line window
                clear()

                if len(new_game.player.get_fishing_rods_owned()) == 0:
                    pass  # Do nothing
                else:
                    print("Below is a list of fishing rods you have:\n")
                    for fishing_rod in new_game.player.get_fishing_rods_owned():
                        print(str(fishing_rod) + "\n")

                    fishing_rod_index: int = int(input("Please enter index of fishing rod you want to equip: "))
                    while fishing_rod_index < 0 or fishing_rod_index >= len(new_game.player.get_fishing_rods_owned()):
                        fishing_rod_index = int(input("Sorry, invalid input! "
                                                      "Please enter index of fishing rod you want to equip: "))

                    to_equip: FishingRod = new_game.player.get_fishing_rods_owned()[fishing_rod_index]
                    new_game.player.add_fishing_rod(to_equip)

            elif action == "UNEQUIP FISHING ROD":
                # Clearing up the command line window
                clear()

                if isinstance(new_game.player.fishing_rod, FishingRod):
                    new_game.player.remove_fishing_rod()
                else:
                    pass  # Do nothing

            elif action == "VIEW STATS":
                # Clearing up the command line window
                clear()

                print(str(new_game.player))

        print("Enter 'Y' for yes.")
        print("Enter anything else for no.")
        continue_playing = input("Do you want to continue playing 'Fishing Tycoon'? ")

    # Saving game data and quitting the game
    save_game_data(new_game, file_name)
    sys.exit()


if __name__ == '__main__':
    main()

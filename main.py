# This is a sample Python script.
import random
from abc import ABC
from dataclasses import dataclass
from typing import Type


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


class Ship(ABC):
    def __init__(self, maneuverability, cannons, crew, hull, mast, cargo, has_long_shot):
        self.maneuverability = maneuverability
        self.cannons = cannons
        self.crew = crew
        self.hull = hull
        self.mast = mast
        self.cargo = cargo
        self.has_long_shot = has_long_shot

    def hit_cannons(self):
        if self.cannons > 0:
            self.cannons -= 1
        else:
            self.hull -= 1

    def hit_crew(self):
        if self.crew > 0:
            self.crew -= 1
        else:
            self.hull -= 1

    def hit_cargo(self):
        if self.cargo > 0:
            self.cargo -= 1
        else:
            self.hull -= 1

    def hit_mast(self):
        if self.mast > 0:
            self.mast -= 1
        else:
            self.hull -= 1

    def copy(self):
        return Ship(self.maneuverability, self.cannons, self.crew, self.hull, self.mast, self.cargo, self.has_long_shot)


@dataclass
class Captain:
    seamanship: int
    scouting: int
    leadership: int
    influence: int


class Sloop(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=4, cannons=1, crew=2, hull=2, mast=2, cargo=2, has_long_shot=has_long_shot)


class Flute(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=2, cannons=1, crew=1, hull=3, mast=3, cargo=4, has_long_shot=has_long_shot)


class Frigate(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=3, cannons=3, crew=3, hull=3, mast=3, cargo=3, has_long_shot=has_long_shot)


class Galeon(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=1, cannons=4, crew=4, hull=4, mast=4, cargo=5, has_long_shot=has_long_shot)


# write a function to generate an array of n random numbers between 1 and 6
def roll_dice(n):
    roll = [random.randint(1, 6) for _ in range(n)]
    success = 0
    tiebreaker = 0
    for i in range(n):
        if roll[i] >= 5:
            success += 1
        else:
            tiebreaker += roll[i]
    return success, tiebreaker


def initiative(captain, ship, defense_ship=None, average_manoeuvre=False):
    if ship.mast < 1:
        return 1
    if not average_manoeuvre:
        if ship.maneuverability >= defense_ship.maneuverability + 2:
            return captain.seamanship + 1
        return captain.seamanship
    else:
        return int((captain.seamanship + ship.maneuverability) / 2.0 + 0.5)


def cannon_fire(attack_ship: Ship, defense_ship: Ship, successes: int):
    n = min(successes, attack_ship.cannons)
    defense_ship = defense_ship.copy()
    for _ in range(n):
        hit = random.randint(1, 6)
        if hit == 1:
            defense_ship.hit_mast()
        if hit == 2:
            defense_ship.hit_crew()
        if hit == 3:
            defense_ship.hit_cargo()
        if hit == 4:
            defense_ship.hit_cannons()
        if hit > 4:
            if defense_ship.cargo > 0:
                defense_ship.hit_cargo()
            else:
                if defense_ship.mast >= max(defense_ship.crew, defense_ship.cannons):
                    defense_ship.hit_mast()
                else:
                    if defense_ship.crew > 0:
                        defense_ship.hit_crew()
                    elif defense_ship.cannons > 0:
                        defense_ship.hit_cannons()
                    else:
                        defense_ship.hull -= 1
    return defense_ship


def long_shot(attack_ship: Ship, defense_ship: Ship, attack_captain: Captain):
    if attack_ship.has_long_shot:
        attack_success, _ = roll_dice(initiative(attack_captain, attack_ship))
        return cannon_fire(attack_ship, defense_ship, attack_success)
    return defense_ship


def battle(attack_ship: Ship, defense_ship: Ship, attack_captain: Captain, defense_captain: Captain,
           use_tiebreaker=True, average_manoeuvre=False, defender_hook_boarding=False, defender_fleeing=False):
    new_defense_ship = long_shot(attack_ship, defense_ship, attack_captain)
    new_attack_ship = long_shot(defense_ship, attack_ship, defense_captain)

    attack_ship = new_attack_ship
    defense_ship = new_defense_ship

    battle_over = False
    round = 1
    while attack_ship.hull > 0 and defense_ship.hull > 0 and not battle_over:
        attacker_dice = initiative(attack_captain, attack_ship, defense_ship, average_manoeuvre)
        attack_success, attack_tie = roll_dice(attacker_dice)
        defender_dice = initiative(defense_captain, defense_ship, attack_ship, average_manoeuvre)
        defense_success, defense_tie = roll_dice(defender_dice)
        if round == 2 and defender_hook_boarding:
            defense_success2, defense_tie = roll_dice(defender_dice - defense_success)
            defense_success += defense_success2

        if attack_success > defense_success:
            attack_hits = attack_ship.cannons
            defense_hits = defense_success
        elif attack_success < defense_success:
            defense_hits = defense_ship.cannons
            attack_hits = attack_success
        else:
            if use_tiebreaker:
                if attack_tie > defense_tie:
                    attack_hits = attack_ship.cannons
                    defense_hits = defense_success
                elif attack_tie < defense_tie:
                    defense_hits = defense_ship.cannons
                    attack_hits = attack_success
                else:
                    attack_hits = attack_success
                    defense_hits = defense_success
            else:
                attack_hits = attack_success
                defense_hits = defense_success

        new_defense_ship = cannon_fire(attack_ship, defense_ship, attack_hits)
        if ((round!=2 or not defender_hook_boarding) and (round == 1 or not defender_fleeing)) or defense_ship.mast == 0:
            new_attack_ship = cannon_fire(defense_ship, attack_ship, defense_hits)
        else:
            new_attack_ship = attack_ship.copy()
            if defender_fleeing:
                # defender fleeing
                if (defense_success > attack_success) or (
                        defense_success == attack_success and defense_tie > attack_tie):
                    if attack_success == 0:
                        battle_over = True  # defender flees
            else:
                # defender attempts boarding (round==2 and defender_hook_boarding)
                if (defense_success > attack_success) or (defense_success == attack_success and defense_tie > attack_tie):
                    if defense_ship.crew > 0 and defense_ship.hull > 0:
                        attacker_result, defender_result = boarding(attack_ship, defense_ship, attack_captain, defense_captain)
                        new_attack_ship.hull = min(new_attack_ship.hull, attacker_result)
                        new_defense_ship.hull = min(new_defense_ship.hull, defender_result)


        attack_ship = new_attack_ship
        defense_ship = new_defense_ship

        if attack_ship.cannons <= 0 and defense_ship.cannons <= 0:
            battle_over = True
        round += 1

    return attack_ship, defense_ship


def boarding(attack_ship: Ship, defense_ship: Ship, attack_captain: Captain, defense_captain: Captain):
    while attack_ship.crew > 0 and defense_ship.crew > 0:
        attack_roll, _ = roll_dice(attack_captain.leadership)
        attack_roll = min(attack_roll, attack_ship.crew)
        defense_roll, _ = roll_dice(defense_captain.leadership)
        defense_roll = min(defense_roll, defense_ship.crew)

        attack_ship.crew -= defense_roll
        defense_ship.crew -= attack_roll

    return attack_ship.crew, defense_ship.crew

def simulate_battle(attack_class: Type[Ship], defense_class: Type[Ship], attack_captain: Captain,
                    defense_captain: Captain,
                    n=10000, attack_long_shot=False, defense_long_shot=False, use_tiebreaker=True,
                    average_manoeuvre=False,
                    defender_hook_boarding=False,
                    defender_fleeing=False):
    attacker_won = 0
    defender_won = 0
    mutual_destruction = 0
    both_survived = 0

    for _ in range(n):
        attack_ship = attack_class(has_long_shot=attack_long_shot)
        defense_ship = defense_class(has_long_shot=defense_long_shot)
        attack_ship, defense_ship = battle(attack_ship, defense_ship, attack_captain, defense_captain,
                                           use_tiebreaker, average_manoeuvre, defender_hook_boarding, defender_fleeing)
        if attack_ship.hull > 0 and defense_ship.hull <= 0:
            attacker_won += 1
        elif defense_ship.hull > 0 and attack_ship.hull <= 0:
            defender_won += 1
        elif defense_ship.hull <= 0 and attack_ship.hull <= 0:
            mutual_destruction += 1
        else:
            both_survived += 1
    print(f"Attacker won: {attacker_won}")
    print(f"Defender won: {defender_won}")
    print(f"Mutual destruction: {mutual_destruction}")
    print(f"Both survived: {both_survived}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    # s = Sloop(has_long_shot=True)
    simulate_battle(attack_class=Frigate,
                    defense_class=Frigate,
                    attack_captain=Captain(3, 3, 3, 3),
                    defense_captain=Captain(2, 3, 3, 3),
                    use_tiebreaker=True,
                    average_manoeuvre=False,
                    defender_hook_boarding=False,
                    defender_fleeing=False,
                    )

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# This is a sample Python script.
import random
from abc import ABC
from dataclasses import dataclass
import numpy as np


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


class Ship(ABC):
    def __init__(self, maneuverability, cannons, crew, hull, mast, cargo, has_long_shot, size=4):
        self.maneuverability = maneuverability
        self.cannons = cannons
        self.crew = crew
        self.hull = hull
        self.mast = mast
        self.cargo = cargo
        self.has_long_shot = has_long_shot
        self.base_manoeuvrability = maneuverability
        self.size = size

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
        self.maneuverability = self.base_manoeuvrability

    def copy(self):
        ship = Ship(self.maneuverability, self.cannons, self.crew, self.hull, self.mast, self.cargo, self.has_long_shot)
        ship.base_manoeuvrability = self.base_manoeuvrability
        return ship


@dataclass
class Captain:
    seamanship: int
    scouting: int
    leadership: int
    influence: int


class Sloop(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=4, cannons=1, crew=2, hull=2, mast=2, cargo=2, has_long_shot=has_long_shot,
                         size=2)


class Flute(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=2, cannons=1, crew=1, hull=3, mast=3, cargo=4, has_long_shot=has_long_shot,
                         size=2)


class Brig(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=3, cannons=2, crew=2, hull=2, mast=2, cargo=4, has_long_shot=has_long_shot,
                         size=2)


class Brig4(Brig):
    def __init__(self, has_long_shot=False):
        super().__init__(has_long_shot=has_long_shot)
        self.maneuverability = 4
        self.base_manoeuvrability = 3


class Frigate(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=3, cannons=3, crew=3, hull=3, mast=3, cargo=3, has_long_shot=has_long_shot,
                         size=3)


class Frigate4(Frigate):
    def __init__(self, has_long_shot=False):
        super().__init__(has_long_shot=has_long_shot)
        self.maneuverability = 4
        self.base_manoeuvrability = 3


class Galeon(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=2, cannons=4, crew=4, hull=4, mast=4, cargo=5, has_long_shot=has_long_shot)


class Galeon3(Galeon):
    def __init__(self, has_long_shot=False):
        super().__init__(has_long_shot=has_long_shot)
        self.maneuverability = 3
        self.base_manoeuvrability = 2


class ManOWar(Ship):
    def __init__(self, has_long_shot=False):
        super().__init__(maneuverability=2, cannons=5, crew=5, hull=5, mast=5, cargo=3, has_long_shot=has_long_shot)


# write a function to generate an array of n random numbers between 1 and 6
def roll_dice(n):
    if n < 1:
        return 0, []
    roll = [random.randint(1, 6) for _ in range(n)]
    success = 0
    tiebreaker = []
    for i in range(n):
        if roll[i] >= 5:
            success += 1
        else:
            tiebreaker.append(roll[i])
    return success, np.sort(tiebreaker)


def initiative(captain, ship, defense_ship, average_manoeuvre=False, reroll_rule=False):
    if ship.mast < 1:
        return 1
    if reroll_rule:
        return ship.maneuverability
    if not average_manoeuvre:
        if ship.maneuverability >= defense_ship.maneuverability + 2:
            return captain.seamanship + 1
        return captain.seamanship
    else:
        return int((captain.seamanship + ship.maneuverability) / 2.0 + 0.5)


def seamanship_contest(captain, ship, defense_ship, average_manoeuvre=False, reroll_rule=False):
    n_dice = initiative(captain, ship, defense_ship, average_manoeuvre, reroll_rule)
    success, tie = roll_dice(n_dice)
    if reroll_rule:
        n_reroll = min(n_dice - success, captain.seamanship)
        success2, tie2 = roll_dice(n_reroll)
        old = n_dice - success - n_reroll
        if old > 0:
            attack_tie = np.concatenate([tie2, tie[-old:]])
        else:
            tie = tie2
        success += success2
    return success, np.sum(tie), n_dice


def cannon_fire(attack_ship: Ship, defense_ship: Ship, successes: int):
    n = min(successes, attack_ship.cannons)  # , defense_ship.size)
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


def do_boarding(attack_ship: Ship, defense_ship: Ship, attack_captain: Captain, defense_captain: Captain):
    if attack_ship.crew > 0 and attack_ship.hull > 0:
        return crew_combat(attack_ship, defense_ship, attack_captain, defense_captain)
    return attack_ship.hull, defense_ship.hull


def long_shot(attack_ship: Ship, defense_ship: Ship):
    if attack_ship.has_long_shot:
        attack_success, _ = roll_dice(attack_ship.cannons)
        return cannon_fire(attack_ship, defense_ship, attack_success)
    return defense_ship


def battle(attack_ship: Ship, defense_ship: Ship, attack_captain: Captain, defense_captain: Captain,
           use_tiebreaker=True, average_manoeuvre=False, defender_hook_boarding=False, defender_fleeing=False,
           reroll_rule=False, attacker_boarding=False):
    new_defense_ship = long_shot(attack_ship, defense_ship)
    new_attack_ship = long_shot(defense_ship, attack_ship)

    attack_ship = new_attack_ship
    defense_ship = new_defense_ship

    battle_over = False
    round = 1
    save_hooks = False
    while attack_ship.hull > 0 and defense_ship.hull > 0 and not battle_over:
        attack_success, attack_tie, _ = seamanship_contest(attack_captain, attack_ship, defense_ship, average_manoeuvre,
                                                           reroll_rule)
        defense_success, defense_tie, defender_dice = seamanship_contest(defense_captain, defense_ship, attack_ship,
                                                                         average_manoeuvre, reroll_rule)
        if round == 2 and defender_hook_boarding:
            if defense_success == defender_dice or attack_success > defender_dice:
                # if all dice are hits or no chance of success, safe hooks for next round
                save_hooks = True
            else:
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

        if round == 1 or not attacker_boarding:
            new_defense_ship = cannon_fire(attack_ship, defense_ship, attack_hits)
        else:
            new_defense_ship = defense_ship.copy()
            # attacker attempts boarding
            if (attack_success > defense_success) or (
                    attack_success == defense_success and attack_tie > defense_tie):
                new_attack_ship.hull, new_defense_ship.hull = do_boarding(new_attack_ship, new_defense_ship,
                                                                          attack_captain, defense_captain)
        if ((round != 2 or not defender_hook_boarding) and (
                round == 1 or not defender_fleeing)) or defense_ship.mast == 0:
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
                if (defense_success > attack_success) or (
                        defense_success == attack_success and defense_tie > attack_tie):
                    new_attack_ship.hull, new_defense_ship.hull = do_boarding(new_attack_ship, new_defense_ship,
                                                                              attack_captain, defense_captain)
        attack_ship = new_attack_ship
        defense_ship = new_defense_ship

        if attack_ship.cannons <= 0 and defense_ship.cannons <= 0:
            battle_over = True
        round += 1
        if round == 3 and save_hooks:
            round = 2
            save_hooks = False
    return attack_ship, defense_ship


def crew_combat(attack_ship: Ship, defense_ship: Ship, attack_captain: Captain, defense_captain: Captain):
    while attack_ship.crew > 0 and defense_ship.crew > 0:
        attack_roll, _ = roll_dice(attack_captain.leadership)
        attack_roll = min(attack_roll, attack_ship.crew)
        defense_roll, _ = roll_dice(defense_captain.leadership)
        defense_roll = min(defense_roll, defense_ship.crew)

        attack_ship.crew -= defense_roll
        defense_ship.crew -= attack_roll

    return attack_ship.crew, defense_ship.crew


def simulate_battle(attack_ship: Ship, defense_ship: Ship, attack_captain: Captain,
                    defense_captain: Captain,
                    n=10000, use_tiebreaker=True,
                    average_manoeuvre=False,
                    defender_hook_boarding=False,
                    defender_fleeing=False,
                    reroll_rule=False, attacker_boarding=False):
    attacker_won = 0
    defender_won = 0
    mutual_destruction = 0
    both_survived = 0

    for _ in range(n):
        a_ship = attack_ship.copy()
        d_ship = defense_ship.copy()
        a_ship, d_ship = battle(a_ship, d_ship, attack_captain, defense_captain,
                                use_tiebreaker, average_manoeuvre, defender_hook_boarding,
                                defender_fleeing, reroll_rule, attacker_boarding=attacker_boarding)
        if a_ship.hull > 0 and d_ship.hull <= 0:
            attacker_won += 1
        elif d_ship.hull > 0 and a_ship.hull <= 0:
            defender_won += 1
        elif d_ship.hull <= 0 and a_ship.hull <= 0:
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

    for fleeing in [True, False]:
        simulate_battle(attack_ship=Galeon(),
                        defense_ship=Galeon(),
                        attack_captain=Captain(1, 3, 2, 3),
                        defense_captain=Captain(2, 3, 2, 3),
                        use_tiebreaker=True,
                        average_manoeuvre=False,
                        defender_hook_boarding=False,
                        defender_fleeing=fleeing,
                        reroll_rule=True,
                        attacker_boarding=False)
        print()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

from utility_functions import *
import numpy as np
import logging
logger = logging.getLogger(__name__)
from typing import List, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from Weapon import Weapon
    from Engagement import Engagement


class Model:
    def __init__(
            self,
            name: str,
            movement: int,
            toughness: int,
            save: int,
            invulnerable_save: int | None,
            wounds: int,
            leadership: int,
            objective_control: int,
            ranged_weapons: Dict[str, 'Weapon'],
            melee_weapons: Dict[str, 'Weapon'],
            abilities: List,
            faction: List[str],
            keywords: List[str],
            faction_keywords: List[str]
    ):
        self.name = name
        self.movement = movement
        self.toughness = toughness
        self.save = save
        self.invulnerable_save = invulnerable_save
        self.wounds = wounds
        self.leadership = leadership
        self.objective_control = objective_control
        self.melee_weapons = melee_weapons
        self.ranged_weapons = ranged_weapons
        self.abilities = abilities
        self.faction = faction
        self.keywords = keywords
        self.faction_keywords = faction_keywords

    def save_roll(self, num_wounds: int, num_crit_wounds: int, weapon: 'Weapon', engagement: 'Engagement') -> int:
        wounds_taken = 0
        # No save vs mortal wounds so crit wounds score direct damage, and then we only consider the normal wounds
        if 'devastating_wounds' in weapon.keywords:
            wounds_taken += num_crit_wounds
            num_wounds -= num_crit_wounds

        rolls = np.random.randint(1, 7, num_wounds)
        wounds_taken += (rolls == 1).sum() # Unmodified rolls of 1 always fail
        rolls = rolls[(rolls != 1)] # Exclude auto failed rolls

        normal_save = self.save
        if 'ignores_cover' in weapon.keywords:
            engagement.in_cover = False
        # make sure cover only works vs shooting
        if engagement.in_cover and weapon.weapon_range > 1:
            if normal_save >= 4 or weapon.armor_piercing > 0:
                normal_save += 1

        # Make sure save wasn't incremented by more than 1
        if normal_save > (self.save + 1):
            normal_save = self.save + 1
        # Select between normal and invulnerable save
        save_used = min(normal_save + weapon.armor_piercing, self.invulnerable_save)
        rolls -= weapon.armor_piercing
        wounds_taken += (rolls >= save_used).sum()
        return wounds_taken

    def take_damage(self, damage_taken: int):
        damage_taken -= feel_no_pain(damage_taken, self.keywords)
        self.wounds -= damage_taken
        if self.wounds < 1:
            print(f'Alas, death claims {self.name}!')


    # save rolls
    # devastating wounds - crit wounds inflict mortal wounds (that cannot be saved against)
    # ignores cover - target gets no benefit from cover
    # precision - when targeting an attached unit, the attacker
    #   can choose to allocate a successful wound to the character

    # damage
    # melta X - increase damage by x if distance to target is less than
    #   half of the range of the weapon
    # feel_no_pain_x - roll D6 for every wound. If the roll >= X, the wound isn't lost



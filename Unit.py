from math import ceil
from collections import defaultdict
from copy import deepcopy
import logging
logger = logging.getLogger(__name__)
from typing import List, Tuple, Set, TYPE_CHECKING
if TYPE_CHECKING:
    from Model import Model
    from Engagement import Engagement
    from Weapon import Weapon


class Unit:
    def __init__(
            self,
            name: str,
            models: List['Model'],
            point_cost: int,
            in_melee_with: List['Unit']
    ):
        self.name = name
        self.models = models
        self.point_cost = point_cost
        self.total_objective_control = sum([model.objective_control for model in self.models])
        self.in_melee_with = in_melee_with
        self.last_action = None
        self.alive = True

    def __mul__(self, count: int) -> List:
        """Return a list of independent copies of this item"""
        if not isinstance(count, int) or count < 0:
            raise ValueError('Can only multiply items by non-negative integers')
        return [deepcopy(self) for _ in range(count)]

    def __rmul__(self, count: int):
        """Support reverse multiplication (3 * item)"""
        return self.__mul__(count)

    def allocate_wounds(self, num_wounds: int, damage_per_wound: int):
        while num_wounds > 0 and self.models:
            # Find first model that can take damage
            model = next((model for model in self.models if model.current_wounds < model.starting_wounds), self.models[0])

            total_absorbable_wounds = ceil(model.current_wounds / damage_per_wound) # How many wounds can the model take?
            wounds_to_apply = min(total_absorbable_wounds, num_wounds)

            model.take_damage(wounds_to_apply * damage_per_wound)
            if not model.alive:
                self.models.remove(model)
                self.total_objective_control -= model.objective_control

            num_wounds -= wounds_to_apply

        if not self.models:
            logger.debug(f'Alas, death claims {self.name}!')
            self.alive = False

    def do_saves(self, num_wounds: int, num_crit_wounds: int, weapon: 'Weapon', engagement: 'Engagement') -> int:
        model = next((model for model in self.models if model.current_wounds < model.starting_wounds), self.models[0])
        return model.save_roll(num_wounds, num_crit_wounds, weapon, engagement)

    def get_toughness(self) -> int:
        # TODO - fix model selection so it takes one of the bodyguards. With current logic, if the leader gets tapped
        #  once via precision, everything following will go to him again
        model = next((model for model in self.models if model.current_wounds < model.starting_wounds), self.models[0])
        return model.toughness

    def select_weapon(self, model: 'Model') -> 'Weapon':
        # TODO get a weapon selection logic
        weapon_name = list(model.ranged_weapons.keys())[0]
        return model.ranged_weapons[weapon_name]

    def get_all_models_keywords(self) -> Set:
        return {keyword for model in self.models for keyword in model.keywords}

    def shoot(self, engagement: 'Engagement') -> defaultdict[str, List[int]]:
        # total_wounds, total_crit_wounds = 0, 0
        wounds_per_weapon = defaultdict(lambda: [0, 0])
        for i, model in enumerate(self.models):
            logger.debug(f'Shooting with: {model.name} ({i+1}/{len(self.models)})')
            weapon = self.select_weapon(model)
            # wounds, crit_wounds = model.ranged_weapons[weapon].wound_roll(engagement, model)
            wounds, crit_wounds = weapon.wound_roll(engagement, model, self)
            # total_wounds += wounds
            # total_crit_wounds += crit_wounds
            if wounds > 0:
                wounds_per_weapon[weapon.name][0] += wounds
                wounds_per_weapon[weapon.name][1] += crit_wounds

        return wounds_per_weapon





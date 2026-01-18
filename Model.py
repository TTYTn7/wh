from utility_functions import *
import logging
logger = logging.getLogger(__name__)
from typing import List, Dict, Set, TYPE_CHECKING
if TYPE_CHECKING:
    from Weapon import Weapon
    from Engagement import Engagement
    from Unit import Unit


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
            keywords: Set[str],
            faction_keywords: List[str],
            in_melee_with: List['Unit'] # Each unit on the battlefield should get a unique identifier so we can keep track
    ):
        self.name = name
        self.movement = movement
        self.toughness = toughness
        self.save = save
        self.invulnerable_save = invulnerable_save
        self.starting_wounds = wounds
        self.current_wounds = wounds
        self.leadership = leadership
        self.objective_control = objective_control
        self.melee_weapons = melee_weapons
        self.ranged_weapons = ranged_weapons
        self.abilities = abilities
        self.faction = faction
        self.keywords = keywords
        self.faction_keywords = faction_keywords
        self.alive = True
        self.in_melee_with = in_melee_with
        self.last_action = None

    def can_shoot(self, weapon: 'Weapon', engagement: 'Engagement') -> bool:
        if self.last_action == 'advanced' and 'assault' not in weapon.keywords:
            logger.debug(
                f'Cannot attack because the weapon wielder advanced and the weapon has no assault capabilities. '
                f'Weapon keywords: {weapon.keywords}.'
            )
            return False
        if self.last_action == 'fall_back':
            logger.debug('Cannot attack because the weapon wielder fell back.')
            return False
        if engagement.distance > weapon.weapon_range:
            logger.debug(
                f'Cannot attack because the distance to target ({engagement.distance}) is larger than '
                f'the weapon\'s range ({weapon.weapon_range}).'
            )
            return False
        if not engagement.line_of_sight and 'indirect_fire' not in weapon.keywords:
            logger.debug(
                f'Cannot attack because target is beyond line of sight and the weapon has no indirect fire capabilities. '
                f'Weapon keywords: {weapon.keywords}.'
            )
            return False

        if 'blast' in weapon.keywords:
            if engagement.opponent.in_melee_with:
                logger.debug(
                    f'Cannot shoot because weapon has the \'blast\' keyword and target is engaged with an ally.'
                    f'Weapon keywords: {weapon.keywords}.'
                )
                return False

        # If in melee (and not a monster of vehicle), we can only shoot the enemy we're in melee with, and only with a pistol
        if self.in_melee_with and not any(keyword in self.keywords for keyword in ['monster', 'vehicle']):
            if 'pistol' not in weapon.keywords:
                logger.debug(
                    f'Cannot shoot because model is in melee and weapon is not a pistol.'
                    f'Weapon keywords: {weapon.keywords}.'
                )
                return False
            if engagement.opponent not in self.in_melee_with: # TODO - make sure this works. E.g. UID on Unit level, that gets passed to Models in that unit? Or at least to this method?
                logger.debug(f'Cannot shoot this target because model is in melee with a different target.')
                return False
            logger.debug(
                f'Can shoot because model is in melee with the target and has a pistol.'
                f'Weapon keywords: {weapon.keywords}.'
            )
            return True

        # If we arent in melee, then we need to consider if opponent is in melee
        if engagement.opponent.in_melee_with:
            if not any(keyword in engagement.opponent.keywords for keyword in ['monster', 'vehicle']):
                logger.debug(
                    f'Cannot shoot because target is engaged and is not a monster or a vehicle.'
                    f'Target keywords: {engagement.opponent.keywords}'
                )
                return False

        return True

    def save_roll(self, num_wounds: int, num_crit_wounds: int, weapon: 'Weapon', engagement: 'Engagement') -> int:
        if num_wounds == 0:
            logger.debug('No wounds to save.')
            return 0
        wounds_taken = 0
        # No save vs mortal wounds so crit wounds score direct damage, and then we only consider the normal wounds
        if 'devastating_wounds' in weapon.keywords:
            wounds_taken += num_crit_wounds
            num_wounds -= num_crit_wounds
            logger.debug(f'Suffering {num_crit_wounds} mortal wounds due to {num_crit_wounds} critical wounds from a \
             weapon with the devastating wounds keyword. Remaining wounds to resolve: {num_wounds}')

        rolls = roll(num_wounds)
        crit_fails = (rolls == 1).sum() # Unmodified rolls of 1 always fail
        wounds_taken += crit_fails
        logger.debug(f'Initial save rolls: {rolls}. Critical fails: {crit_fails}. Reminder rolls: {rolls[(rolls != 1)]}')
        rolls = rolls[(rolls != 1)] # Exclude auto failed rolls

        normal_save = self.save
        if 'ignores_cover' in weapon.keywords:
            engagement.in_cover = False
        # make sure cover only works vs shooting
        if engagement.in_cover and weapon.weapon_range > 1:
            if normal_save >= 4 or weapon.armor_piercing > 0:
                rolls += 1
                logger.debug(f'Due to the target being in cover, rolls receive a +1 modifier. New rolls: {rolls}')

        # Make sure save wasn't incremented by more than 1
        if normal_save > (self.save + 1):
            normal_save = self.save + 1
        # Select between normal and invulnerable save
        if normal_save + weapon.armor_piercing < self.invulnerable_save:
            save_used = normal_save
        else:
            save_used = self.invulnerable_save
        logger.debug(
            f'{self.name}\'s save characteristic used: {save_used}. '
        )
        rolls -= weapon.armor_piercing
        wounds_taken += (rolls < save_used).sum()
        logger.debug(
            f'Armor piercing: {weapon.armor_piercing}. Final roll values: {rolls}, resulting in {wounds_taken} '
            f'successful instances of damage.'
        )
        return wounds_taken

    def take_damage(self, damage_taken: int):
        damage_taken -= feel_no_pain(damage_taken, self.keywords)
        self.current_wounds -= damage_taken
        if self.current_wounds < 1:
            logger.debug(f'Alas, death claims {self.name}!')
            self.alive = False


    # save rolls
    # devastating wounds - crit wounds inflict mortal wounds (that cannot be saved against)
    # ignores cover - target gets no benefit from cover
    # precision - when targeting an attached unit, the attacker
    #   can choose to allocate a successful wound to the character

    # damage
    # melta X - increase damage by x if distance to target is less than
    #   half of the range of the weapon
    # feel_no_pain_x - roll D6 for every wound. If the roll >= X, the wound isn't lost



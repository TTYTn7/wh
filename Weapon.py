# Weapons
from utility_functions import *
import logging
logger = logging.getLogger(__name__)
from typing import Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from Engagement import Engagement
    from Model import Model


class Weapon:
    def __init__(
            self,
            name: str,
            weapon_range: int,
            attacks: int | str,
            ballistic_skill: int,
            strength: int,
            armor_piercing: int,
            damage: int,
            keywords: Set[str]
    ):
        self.name = name
        self.weapon_range = weapon_range
        self.attacks = attacks
        self.ballistic_skill = ballistic_skill
        self.strength = strength
        self.armor_piercing = armor_piercing
        self.damage = damage
        self.keywords = keywords

    def get_num_attacks(self, engagement: 'Engagement'):
        if 'D' in str(self.attacks).upper():
            num_attacks = roll(int(self.attacks[1]))
        else:
            num_attacks = self.attacks
        num_attacks += rapid_fire(self.weapon_range, self.keywords, engagement.distance)
        if 'blast' in self.keywords:
            num_attacks += blast(engagement)
        return num_attacks

    def hit_roll(self, engagement: 'Engagement') -> Tuple[int, int]:
        num_attacks = self.get_num_attacks(engagement)
        logger.debug(f'Weapon number of attacks: {num_attacks}.')
        if 'torrent' in self.keywords:
            logger.debug('All attacks automatically hit due to the weapon having the "torrent" keyword.')
            return num_attacks, 0

        rolls = roll(num_attacks)
        num_crit_hits, rolls = handle_crits(rolls, 1, 6)
        if not engagement.line_of_sight: # implied that the weapon has 'indirect_fire' keyword, else would have failed the self.can_attack(engagement) check
            rolls = rolls[(rolls > 3)]
            rolls -= 1

        if 'heavy' in self.keywords:
            rolls = heavy(rolls, engagement)

        logger.debug(f'Hit requirement is {self.ballistic_skill}')
        num_hits = (rolls >= self.ballistic_skill).sum() + num_crit_hits
        num_hits += sustained_hits(num_crit_hits, self.keywords)
        logger.debug(f'Hits: {num_hits}, of which Crits: {num_crit_hits}')
        return num_hits, num_crit_hits

    def wound_roll(self, engagement: 'Engagement', wielder: 'Model') -> Tuple[int, int] | None:
        if not wielder.can_shoot(self, engagement):
            return None
        num_hits, num_crit_hits = self.hit_roll(engagement)
        if num_hits == 0:
            return 0, 0

        num_wounds = 0
        if 'lethal_hits' in self.keywords:  # crit hits automatically become wounds
            num_wounds, num_hits = lethal_hits(num_hits, num_crit_hits)

        wound_roll_requirement = find_wound_roll_requirement(self.strength, engagement.opponent.toughness)
        logger.debug(
            f'Wound roll requirement is {wound_roll_requirement} due to weapon strength being {self.strength} and '
            f'opponent toughness being {engagement.opponent.toughness}.'
        )

        rolls = roll(num_hits)
        if 'twin-linked' in self.keywords:
            rolls = twin_linked(rolls, wound_roll_requirement)

        crit_success_boundary = anti_keyword(self.keywords, engagement.opponent.keywords)
        num_crit_wounds, rolls = handle_crits(rolls, fail_boundary=1, success_boundary=crit_success_boundary)

        if 'lance' in self.keywords:
            rolls = lance(rolls, engagement)

        if 'hazardous' in self.keywords:
            hazardous(wielder)

        num_wounds += (rolls >= wound_roll_requirement).sum() + num_crit_wounds
        logger.debug(f'Wounds: {num_wounds}, of which Crits: {num_crit_wounds}')
        return num_wounds, num_crit_wounds


    # keywords

    # hit rolls
    # rapid fire X - increase number of attacks by X if distance
    #   to target is less than half of the weapon's range
    # torrent - attacks automatically hit
    # indirect fire - can attack units beyond line of sight
    #   if no models are visible, hit roll gets a -1 penalty
    #   unmodified hit rolls of 1-3 always fail, and the target has cover
    # blast - +1 attack for every 5 models in the target unit (round down)
    #   cannot target enemy unit within engagement range of ally unit
    # heavy - +1 to hit if the bearer remained stationary this turn
    # sustained hits X - add X successful hits for every unmodified critical hit
    #   against the target

    # wounds rolls
    # twin-linked - can re-roll each would roll
    # lethal hits - critical hits automatically wound the target
    # anti Y X - attacks made against Y keyword (e.g. infantry, vehicle), unmodified
    #   wound rolls of X+ score a critical wound
    # lance - if the bearer charged, add 1 to the wound roll

    # save rolls
    # devastating wounds - crit wounds inflict mortal wounds (that cannot be saved against)
    # ignores cover - target gets no benefit from cover
    # melta X - increase damage by x if distance to target is less than
    #   half of the range of the weapon
    # precision - when targeting an attached unit, the attacker
    #   can choose to allocate a successful wound to the character

    # useability
    # assault - can be shot even if the bearer's unit advanced
    # pistol - can shoot even within engagemen range, but must
    #   target the enemy that is also in engagement rage
    # extra attacks - can attack with this weapon in addition to any other weapons
    # blast - +1 attack for every 5 models in the target unit (round down)
    #   cannot target enemy unit within engagement range of ally unit
    # indirect fire - can attack units beyond line of sight
    #   if no models are visible, hit roll gets a -1 penalty
    #   unmodified hit rolls of 1-3 always fail, and the target has cover

    # unique
    # hazardous - after using, roll a D6. On a 1, user suffers 3 mortal wounds


# Weapons
from utility_functions import *
import logging
logger = logging.getLogger(__name__)
from typing import List, Tuple, TYPE_CHECKING
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
            keywords: List[str]
    ):
        self.name = name
        self.weapon_range = weapon_range
        self.attacks = attacks
        self.ballistic_skill = ballistic_skill
        self.strength = strength
        self.armor_piercing = armor_piercing
        self.damage = damage
        self.keywords = keywords

    def can_attack(self, engagement: 'Engagement') -> bool:
        if engagement.last_action == 'advanced' and 'assault' not in self.keywords:
            logger.debug(
                f'Cannot attack because the weapon wielder advanced and the weapon has no assault capabilities. '
                f'Weapon keywords: {self.keywords}.'
            )
            return False
        if engagement.distance > self.weapon_range:
            logger.debug(
                f'Cannot attack because the distance to target ({engagement.distance}) is larger than '
                f'the weapon range ({self.weapon_range}).'
            )
            return False
        if not engagement.line_of_sight and 'indirect_fire' not in self.keywords:
            logger.debug(
                f'Cannot attack because target is beyond line of sight and the weapon has no indirect fire capabilities. '
                f'Weapon keywords: {self.keywords}.'
            )
            return False
        if engagement.distance <= 1 and 'pistol' not in self.keywords:
            logger.debug(
                f'Cannot attack because the target is in melee range and the weapon is not a pistol. '
                f'Weapon keywords: {self.keywords}.'
            )
            return False
        if engagement.engaging_ally and 'blast' in self.keywords:
            logger.debug(
                f'Cannot attack because the weapon has the "blast" keyword and there is an ally unit within the '
                f'target\'s engagement range.'
            )
            return False
        return True

    def get_num_attacks(self, engagement: 'Engagement'):
        if 'D' in str(self.attacks).upper():
            # num_attacks = np.random.randint(1, 7, int(self.attacks[1]))
            num_attacks = roll(int(self.attacks[1]))
        else:
            num_attacks = self.attacks
        num_attacks += rapid_fire(self.weapon_range, self.keywords, engagement.distance)
        if 'blast' in self.keywords:
            num_attacks += (engagement.num_targets // 5)
        return num_attacks

    def hit_roll(self, engagement: 'Engagement') -> Tuple[int, int]:
        num_attacks = self.get_num_attacks(engagement)
        logger.debug(f'Weapon number of attacks: {num_attacks}.')
        if 'torrent' in self.keywords:
            logger.debug('All attacks automatically hit due to the weapon having the "torrent" keyword.')
            return num_attacks, 0

        # rolls =  np.random.randint(1, 7, num_attacks)
        rolls = roll(num_attacks)
        num_crit_hits, rolls = handle_crits(rolls, 1, 6)
        if not engagement.line_of_sight: # implied that the weapon has 'indirect_fire' keyword, else would have failed the self.can_attack(engagement) check
            rolls = rolls[(rolls > 3)]
            rolls -= 1
        if 'heavy' in self.keywords and engagement.last_action == 'remained_stationary':
            rolls += 1
            logger.debug(
                f'Rolls get upgraded due to the wielder having remained stationary and the weapon having the "heavy" '
                f'keyword. Previous rolls: {rolls - 1}, upgraded rolls: {rolls}'
            )

        logger.debug(f'Hit requirement is {self.ballistic_skill}')
        num_hits = (rolls >= self.ballistic_skill).sum() + num_crit_hits
        num_hits += sustained_hits(num_crit_hits, self.keywords)
        logger.debug(f'Hits: {num_hits}, of which Crits: {num_crit_hits}')
        return num_hits, num_crit_hits

    def wound_roll(self, engagement: 'Engagement', wielder: 'Model') -> Tuple[int, int] | None:
        if not self.can_attack(engagement):
            return None

        num_hits, num_crit_hits = self.hit_roll(engagement)
        if num_hits == 0:
            return 0, 0

        num_wounds = 0
        wound_roll_requirement = find_wound_roll_requirement(self.strength, engagement.opponent.toughness)
        logger.debug(
            f'Wound roll requirement is {wound_roll_requirement} due to weapon strength being {self.strength} and '
            f'opponent toughness being {engagement.opponent.toughness}.'
        )

        if 'lethal_hits' in self.keywords: # crit hits automatically become wounds
            num_wounds += num_crit_hits
            num_hits -= num_crit_hits
            logger.debug(
                f'All {num_crit_hits} critical hits automatically become wounds because of the weapon\'s "lethal hits" '
                f'keyword. Only {num_hits} need to be rolled for.'
            )

        # rolls = np.random.randint(1, 7, num_hits)
        rolls = roll(num_hits)
        crit_success_boundary = anti_keyword(self.keywords, engagement.opponent.keywords)

        num_crit_wounds, rolls = handle_crits(rolls, fail_boundary=1, success_boundary=crit_success_boundary)
        if 'lance' in self.keywords and engagement.last_action == 'charged':
            rolls += 1
            logger.debug(
                f'Rolls get upgraded due to the wielder having charged and the weapon having the "lance" keyword. '
                f'Previous rolls: {rolls - 1}, upgraded rolls: {rolls}'
            )

        num_wounds += (rolls >= wound_roll_requirement).sum() + num_crit_wounds
        if 'twin-linked' in self.keywords:
            num_wounds += twin_linked(rolls, wound_roll_requirement)

        if 'hazardous' in self.keywords:
            wielder.wounds -= hazardous()

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


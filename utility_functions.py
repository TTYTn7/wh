import numpy as np
from numpy.typing import NDArray
import logging
logger = logging.getLogger(__name__)
from typing import Tuple, Set, TYPE_CHECKING
if TYPE_CHECKING:
    from Weapon import Weapon
    from Engagement import Engagement
    from Model import Model


def roll(num_rolls: int) -> NDArray[np.integer]:
    return np.random.randint(1, 7, num_rolls)


def re_roll_fails(rolls: NDArray[np.integer], success_boundary: int) -> NDArray[np.integer]:
    num_fails = (rolls < success_boundary).sum()
    successes = rolls[rolls >= success_boundary]
    re_rolls = roll(num_fails)
    return np.concatenate([successes, re_rolls])


def re_roll_ones(rolls: NDArray[np.integer]) -> NDArray[np.integer]:
    return re_roll_fails(rolls, 2)


def handle_crits(rolls: NDArray[np.integer], fail_boundary: int, success_boundary: int) -> Tuple[int, NDArray[np.integer]]:
    logger.debug(
        f'Rolls: {rolls}. Critical fail boundary: {fail_boundary}, critical success boundary: {success_boundary}.'
    )
    crit_fails = (rolls <= fail_boundary)
    crit_successes = (rolls >= success_boundary)
    all_crits = crit_fails | crit_successes
    logger.debug(
        f'Crit fails: {crit_fails} ({crit_fails.sum()}), Crit successes: {crit_successes} ({crit_successes.sum()}).'
    )
    reminder = rolls[~all_crits]
    logger.debug(f'Reminder: {reminder}')
    return crit_successes.sum(), reminder


def find_wound_roll_requirement(strength: int, toughness: int) -> int:
    if strength > toughness:
        if strength >= toughness * 2:
            return 2
        return 3
    elif strength < toughness:
        if strength <= toughness / 2:
            return 6
        return 5
    return 4 # implied that strength == toughness


def calculate_damage(num_wounds_taken: int, weapon: 'Weapon', engagement: 'Engagement') -> int:
    damage = num_wounds_taken * (weapon.damage + melta(weapon.weapon_range, weapon.keywords, engagement.distance))
    logger.debug(f'{num_wounds_taken} wounds at {weapon.damage} damage each deal a total of {damage} damage.')
    return damage


def charge(distance: int, re_roll: str, modifier: int=0) -> bool:
    if re_roll == 'ones':
        charge_roll = re_roll_ones(roll(2)) + modifier
    elif re_roll == 'both':
        charge_roll = roll(2) + modifier
        if charge_roll.sum() < distance:
            charge_roll = roll(2) + modifier
    else:
        charge_roll = roll(2) + modifier
    return charge_roll.sum() >= distance


# Keyword functions:
def get_keyword_x_value(keyword: str | None) -> int:
    if keyword:
        return int(keyword.split('_')[-1])
    return 0


def check_keyword(target_keyword: str, keywords: Set[str]) -> str | None:
    occurrences = [keyword for keyword in keywords if target_keyword in keyword]
    if occurrences:
        return occurrences[0]
    return None # if target keyword not present


def sustained_hits(num_crit_hits: int, keywords: Set[str]) -> int:
    if num_crit_hits == 0:
        return 0
    sustained_hits_keyword_present = check_keyword('sustained_hits', keywords)
    if sustained_hits_keyword_present:
        sustained_hits_value = get_keyword_x_value(sustained_hits_keyword_present)
        added_hits = num_crit_hits * sustained_hits_value
        logger.debug(
            f'Adding {sustained_hits_value} extra hits due to the weapon having {sustained_hits_keyword_present} '
            f'and scoring {num_crit_hits} critical hits (+{sustained_hits_value} extra hits per critical hit).'
        )
        return added_hits
    return 0


def twin_linked(rolls: NDArray[np.integer], wound_roll_requirement: int) -> NDArray[np.integer]:
    re_rolls = re_roll_fails(rolls, wound_roll_requirement)
    logger.debug(
        f'Using twin-linked. Rolls: {rolls} with requirement {wound_roll_requirement}.'
        f'Unsuccessful: {(rolls < wound_roll_requirement).sum()}, Successful: {(rolls >= wound_roll_requirement).sum()}'
        f'Re-rolls: {re_rolls} for a total of {(rolls >= wound_roll_requirement).sum()} successful rolls.'
    )
    return re_rolls


def rapid_fire(weapon_range: int, keywords: Set[str], distance: float) -> int:
    if distance > (weapon_range / 2):
        return 0
    rapid_fire_keyword_present = check_keyword('rapid_fire', keywords)
    if rapid_fire_keyword_present:
        rapid_fire_value = get_keyword_x_value(rapid_fire_keyword_present)
        logger.debug(
            f'Adding {rapid_fire_value} attacks due to distance to opponent ({distance}) being less than half of '
            f'the weapon\'s range ({weapon_range}) and the weapon having the {rapid_fire_keyword_present} keyword.'
        )
        return rapid_fire_value
    return 0


def lethal_hits(num_hits: int, num_crit_hits: int) -> Tuple[int, int]:
    wounds = num_crit_hits
    num_hits -= num_crit_hits
    logger.debug(
        f'All {num_crit_hits} critical hits automatically become wounds because of the weapon\'s "lethal hits" '
        f'keyword. Only {num_hits} need to be rolled for.'
    )
    return wounds, num_hits


def lance(rolls: NDArray[np.integer], engagement: 'Engagement') -> NDArray[np.integer]:
    if engagement.last_action == 'charged':
        upgraded_rolls = rolls + 1
        logger.debug(
            f'Rolls get upgraded due to the wielder having charged and the weapon having the "lance" keyword. '
            f'Previous rolls: {rolls}, upgraded rolls: {upgraded_rolls}'
        )
        return upgraded_rolls
    return rolls


def heavy(rolls: NDArray[np.integer], engagement: 'Engagement') -> NDArray[np.integer]:
    if engagement.last_action == 'remained_stationary':
        upgraded_rolls = rolls + 1
        logger.debug(
            f'Rolls get upgraded due to the wielder having remained stationary and the weapon having the "heavy" keyword. '
            f'Previous rolls: {rolls}, upgraded rolls: {upgraded_rolls}'
        )
        return upgraded_rolls
    return rolls


def blast(engagement: 'Engagement') -> int:
    return engagement.num_targets // 5


def melta(weapon_range: int, keywords: Set[str], distance: float) -> int:
    if distance > (weapon_range / 2):
        return 0
    melta_keyword_present = check_keyword('melta', keywords)
    if melta_keyword_present:
        melta_value = get_keyword_x_value(melta_keyword_present)
        logger.debug(
            f'Adding {melta_value} damage due to distance to opponent ({distance}) being less than half of '
            f'the weapon\'s range ({weapon_range}) and the weapon having the {melta_keyword_present} keyword.'
        )
        return melta_value
    return 0


def anti_keyword(keywords: Set[str], opponent_keywords: Set[str]) -> int:
    anti_keyword_full = check_keyword('anti', keywords)
    if anti_keyword_full:
        target = anti_keyword.split('_')[1]
        if target in opponent_keywords:
            new_crit_success_threshold = get_keyword_x_value(anti_keyword_full)
            logger.debug(
                f'Due to the fact that the weapon has the {anti_keyword_full} keyword and the target has the {target} '
                f'keyword, unmodified wound rolls now crit on {new_crit_success_threshold}+.'
            )
            return new_crit_success_threshold
    return 6


def big_guns_never_tire(attacker_keywords: Set[str], opponent_keywords: Set[str]) -> bool:
    if any(keyword in opponent_keywords for keyword in ['monster', 'vehicle']) \
        or any(keyword in attacker_keywords for keyword in ['monster', 'vehicle']):
        return True
    return False


def feel_no_pain(damage_taken: int, keywords: Set[str]) -> int:
    damage_ignored = 0
    feel_no_pain_full = check_keyword('feel_no_pain', keywords)
    if feel_no_pain_full:
        rolls = roll(damage_taken)
        fnp_boundary = get_keyword_x_value(feel_no_pain_full)
        damage_ignored = (rolls >= fnp_boundary).sum()
        logger.debug(
            f'Ignoring {damage_ignored} out of {damage_taken} damage due to the "Feel No Pain" rule. '
            f'FNP boundary: {fnp_boundary} and rolls: {rolls}'
        )
    return damage_ignored


def hazardous(wielder: 'Model'):
    if 6 in roll(1):
        logger.debug('Weapon exploding because it\'s hazardous and rolled a 6.')
        wielder.take_damage(3)


def deadly_demise(keywords: Set[str]) -> int:
    deadly_demise_full = check_keyword('deadly_demise', keywords)
    if deadly_demise_full:
        if 6 in roll(1):
            explosion_damage = get_keyword_x_value(deadly_demise_full)
            logger.debug(f'Exploding for {explosion_damage} damage in a 6-inch radius!')
            return explosion_damage
    return 0

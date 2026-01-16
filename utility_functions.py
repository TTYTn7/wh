import numpy as np
from numpy.typing import NDArray
import logging
logger = logging.getLogger(__name__)
from typing import List, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from Weapon import Weapon
    from Engagement import Engagement


def roll(num_rolls: int) -> NDArray[np.integer]:
    return np.random.randint(1, 7, num_rolls)


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


def hazardous() -> int:
    # if 6 in np.random.randint(1, 7, 1):
    if 6 in roll(1):
        logger.debug('Weapon exploding because it\'s hazardous and rolled a 6.')
        return 3
    return 0


def get_keyword_x_value(keyword: str | None) -> int:
    if keyword:
        return int(keyword.split('_')[-1])
    return 0


def check_keyword(target_keyword: str, keywords: List[str]) -> str | None:
    occurrences = [keyword for keyword in keywords if target_keyword in keyword]
    if occurrences:
        return occurrences[0]
    return None # if target keyword not present


def sustained_hits(num_crit_hits: int, keywords: List[str]) -> int:
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


def twin_linked(rolls: NDArray[np.integer], wound_roll_requirement: int) -> int:
    num_unsuccessful_rolls = (rolls < wound_roll_requirement).sum()
    # re_rolls = np.random.randint(1, 7, num_unsuccessful_rolls)
    re_rolls = roll(num_unsuccessful_rolls)
    successful_rolls = (re_rolls >= wound_roll_requirement)
    logger.debug(
        f'Using twin-linked. Rolls: {rolls} with requirement {wound_roll_requirement}.'
        f'Number of unsuccessful rolls: {num_unsuccessful_rolls}.'
        f'Re-rolls: {re_rolls}, resulting in additional {successful_rolls.sum()} successful rolls.'
    )
    return successful_rolls.sum()


def rapid_fire(weapon_range: int, keywords: List[str], distance: float) -> int:
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


def melta(weapon_range: int, keywords: List[str], distance: float) -> int:
    if distance > (weapon_range / 2):
        return 0
    melta_keyword_present = check_keyword('melta', keywords)
    if melta_keyword_present:
        melta_value = get_keyword_x_value(melta_keyword_present)
        logger.debug(
            f'Adding {melta_value} attacks due to distance to opponent ({distance}) being less than half of '
            f'the weapon\'s range ({weapon_range}) and the weapon having the {melta_keyword_present} keyword.'
        )
        return melta_value
    return 0


def anti_keyword(keywords: List[str], opponent_keywords: List[str]) -> int:
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


def feel_no_pain(damage_taken: int, keywords: List[str]) -> int:
    damage_ignored = 0
    feel_no_pain_full = check_keyword('feel_no_pain', keywords)
    if feel_no_pain_full:
        # rolls = np.random.randint(1, 7, damage_taken)
        rolls = roll(damage_taken)
        amount_of_pain_not_felt = get_keyword_x_value(feel_no_pain_full)
        damage_ignored = (rolls >= amount_of_pain_not_felt).sum()
        logger.debug(
            f'Ignoring {damage_ignored} out of {damage_taken} damage due to the "Feel No Pain" rule. '
            f'FNP boundary: {amount_of_pain_not_felt} and rolls: {rolls}'
        )
    return damage_ignored


def deadly_demise(keywords: List[str]) -> int:
    deadly_demise_full = check_keyword('deadly_demise', keywords)
    if deadly_demise_full:
        # if 6 in np.random.randint(1, 7, 1):
        if 6 in roll(1):
            explosion_damage = get_keyword_x_value(deadly_demise_full)
            logger.debug(f'Exploding for {explosion_damage} damage in a 6-inch radius!')
            return explosion_damage
    return 0


def calculate_damage(num_wounds_taken: int, weapon: 'Weapon', engagement: 'Engagement') -> int:
    damage = num_wounds_taken * (weapon.damage + melta(weapon.weapon_range, weapon.keywords, engagement.distance))
    logger.debug(f'{num_wounds_taken} wounds at {weapon.damage} damage each deal a total of {damage} damage.')
    return damage

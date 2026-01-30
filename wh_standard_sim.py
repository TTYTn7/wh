from warhammer.datasheets.weapon_collection import weapon_collection
from warhammer.datasheets.model_collection import model_collection
from warhammer.datasheets.unit_collection import unit_collection
from Engagement import Engagement
from Unit import Unit
from Model import Model
from warhammer.utility_functions import calculate_damage
from copy import deepcopy
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # Logs go to this file
    filemode='w'  # 'a' to append, 'w' to overwrite
)
logger = logging.getLogger(__name__)
logger.debug('Log Start')
# TODO check how does the change in ballistic skill change likelihood to land a hit


def shooting_round(attacker: Unit, engagement_details: Engagement):
    defender = engagement_details.opponent
    logger.debug(f'{attacker.name} attacks enemy {defender.name}')
    logger.debug(f'Starting state of defending unit: {[model.current_wounds for model in defender.models]}')
    wounds_per_weapon = attacker.shoot(engagement_details)
    logger.debug(f'Wounds to be allocated pre-saves: {dict(wounds_per_weapon)}') # For cleaner logging
    for weapon_name in wounds_per_weapon:
        num_wounds, num_crit_wounds = wounds_per_weapon[weapon_name]
        logger.debug(f'Resolving for {weapon_name}. Total wounds: {num_wounds}, of which crits: {num_crit_wounds}')

        # roll the saves - select the injured model, roll their saves, see how many wounds go through
        weapon = weapon_collection[weapon_name]
        wounds_taken = defender.do_saves(num_wounds, num_crit_wounds, weapon, engagement_details)
        logger.debug(f'Wounds to be allocated post-saves: {wounds_taken} at {weapon.damage} damage each')
        defender.allocate_wounds(wounds_taken, weapon.damage)

    logger.debug(f'New state of defending unit: {[model.current_wounds for model in defender.models]}')


def multiple_shooting_rounds(num_rounds: int, attacker: Unit, engagement_details: Engagement):
    for i in range(num_rounds):
        if engagement_details.opponent.alive:
            logger.debug('-----------------------------------------------------------------------------------------')
            logger.debug(f'-------------------------------------- Round {i+1} ------------------------------------------')
            logger.debug('-----------------------------------------------------------------------------------------')
            shooting_round(attacker, engagement_details)
        else:
            logger.debug(f'Opponent unit has been wiped out')

# Unit v Unit
# example_terminator_unit = deepcopy(unit_collection['example_terminator_unit'])
# example_terminator_enemy_unit = deepcopy(unit_collection['example_terminator_unit'])
ctan_nightbringer = deepcopy(unit_collection['ctan_shard_of_the_nightbringer'])
# engagement_details = Engagement(distance=3, line_of_sight=True, in_cover=True, opponent=example_terminator_enemy_unit)
# engagement_details = Engagement(distance=7, line_of_sight=True, in_cover=False, opponent=ctan_nightbringer)
allarus_custodes = deepcopy(unit_collection['allarus_custodians'])
engagement_details = Engagement(distance=7, line_of_sight=True, in_cover=False, opponent=allarus_custodes)

multiple_shooting_rounds(4, ctan_nightbringer, engagement_details)

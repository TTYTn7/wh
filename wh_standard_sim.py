from weapon_collection import weapon_collection
from model_collection import model_collection
from unit_collection import unit_collection
from Engagement import Engagement, LastAction
from Unit import Unit
from Model import Model
from Weapon import Weapon
from warhammer.utility_functions import calculate_damage
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # Logs go to this file
    filemode='w'  # 'a' to append, 'w' to overwrite
)

logger = logging.getLogger(__name__)
logger.debug('Log Start')

# Model v Model
example_terminator = model_collection['example_terminator_char']
example_terminator_enemy = model_collection['example_terminator_char']

# engagement_details = Engagement(
#     distance=3, line_of_sight=True, last_action=LastAction.remained_stationary, in_cover=True,
#     engaging_ally=True, num_targets=1, opponent=example_terminator_enemy
# )
engagement_details = Engagement(distance=3, line_of_sight=True, in_cover=True, opponent=example_terminator_enemy)


def round_with_model(attacker: Model, attacking_weapon: str, defender: Model, engagement: Engagement):
    logger.debug(f'{attacker.name} attacks enemy {defender.name} using their {attacking_weapon}')
    wounds, crit_wounds = attacker.ranged_weapons[attacking_weapon].wound_roll(engagement, attacker)
    # Saves
    wounds_taken = defender.save_roll(
        wounds, crit_wounds, attacker.ranged_weapons[attacking_weapon], engagement
    )
    print(f'Wounds taken: {wounds_taken}')

    # Damage
    print(f'Current health: {defender.current_wounds}')
    dmg_to_take = calculate_damage(wounds_taken, attacker.ranged_weapons[attacking_weapon], engagement)
    defender.take_damage(dmg_to_take)
    print(f'Current health: {defender.current_wounds}')
    logger.debug(f'Defender remaining wounds: {defender.current_wounds}')


def multiple_rounds_with_model(num_rounds: int, engagement: Engagement):
    for i in range(num_rounds):
        logger.debug('-----------------------------------------------------------------------------------------')
        logger.debug(f'-------------------------------------- Round {i+1} ------------------------------------------')
        logger.debug('-----------------------------------------------------------------------------------------')
        round_with_model(example_terminator, 'example_rifle', example_terminator_enemy, engagement)


# multiple_rounds_with_model(4, engagement_details)
# TODO check how does the change in ballistic skill change likelihood to land a hit



# Unit v Unit
example_terminator_unit = (unit_collection['example_terminator_unit'] * 1)[0]
example_terminator_enemy_unit = (unit_collection['example_terminator_unit'] * 1)[0]

# unit_engagement_details = Engagement(
#     distance=3, line_of_sight=True, last_action=LastAction.remained_stationary, in_cover=True,
#     engaging_ally=True, num_targets=1, opponent=example_terminator_enemy_unit
# )
unit_engagement_details = Engagement(distance=3, line_of_sight=True, in_cover=True, opponent=example_terminator_enemy_unit)
# TODO - num_targets can be deduced by the model count in the opponent unit
# TODO - engaging ally can also be deduced by the in_melee_with
# TODO - also last_action


def round_with_unit(attacker: Unit, defender: Unit, engagement: Engagement):
    logger.debug(f'{attacker.name} attacks enemy {defender.name}')
    logger.debug(f'Starting state of defending unit: {[model.current_wounds for model in defender.models]}')
    wounds_per_weapon = attacker.shoot(engagement)
    logger.debug(f'Wounds to be allocated pre-saves: {dict(wounds_per_weapon)}') # For cleaner logging
    for weapon_name in wounds_per_weapon: # I.e. for weapon # TODO - ask AI if I should have weapon.name as key, or the weapon instance itself
        num_wounds, num_crit_wounds = wounds_per_weapon[weapon_name]
        logger.debug(f'Resolving for {weapon_name}. Total wounds: {num_wounds}, of which crits: {num_crit_wounds}')

        # roll the saves - select the injured model, roll their saves, see how many wounds go through
        weapon = weapon_collection[weapon_name]
        wounds_taken = defender.do_saves(num_wounds, num_crit_wounds, weapon, engagement)
        logger.debug(f'Wounds to be allocated post-saves: {wounds_taken} at {weapon.damage} damage each')
        defender.allocate_wounds(wounds_taken, weapon.damage)

    logger.debug(f'New state of defending unit: {[model.current_wounds for model in defender.models]}')


def multiple_rounds_with_unit(num_rounds: int, engagement: Engagement):
    for i in range(num_rounds):
        if engagement.opponent.alive:
            logger.debug('-----------------------------------------------------------------------------------------')
            logger.debug(f'-------------------------------------- Round {i+1} ------------------------------------------')
            logger.debug('-----------------------------------------------------------------------------------------')
            round_with_unit(example_terminator_unit, example_terminator_enemy_unit, engagement)
        else:
            logger.debug(f'Opponent unit has been wiped out')

multiple_rounds_with_unit(4, unit_engagement_details)

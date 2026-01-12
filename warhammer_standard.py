from model_collection import model_collection
from Engagement import Engagement, LastAction
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

example_terminator = model_collection['example_terminator_char']
example_terminator_enemy = model_collection['example_terminator_char']

engagement_details = Engagement(
    distance=3, line_of_sight=True, last_action=LastAction.remained_stationary, in_cover=True,
    engaging_ally=True, num_targets=1, opponent=example_terminator_enemy
)

def round(attacker: 'Model', attacking_weapon: 'Weapon', defender: 'Model', engagement: Engagement):
    logger.debug(f'{attacker.name} attacks enemy {defender.name} using their {attacking_weapon}')
    wounds, crit_wounds = attacker.ranged_weapons[attacking_weapon].wound_roll(engagement, attacker)
    # Saves
    wounds_taken = attacker.save_roll(
        wounds, crit_wounds, attacker.ranged_weapons[attacking_weapon], engagement
    )
    print(f'Wounds taken: {wounds_taken}')

    # Damage
    print(f'Current health: {defender.wounds}')
    dmg_to_take = calculate_damage(wounds_taken, attacker.ranged_weapons[attacking_weapon], engagement)
    defender.take_damage(dmg_to_take)
    print(f'Current health: {defender.wounds}')
    logger.debug(f'Defender remaining wounds: {defender.wounds}')


def multiple_rounds(num_rounds: int):
    for i in range(num_rounds):
        logger.debug('-----------------------------------------------------------------------------------------')
        logger.debug(f'-------------------------------------- Round {i+1} ------------------------------------------')
        logger.debug('-----------------------------------------------------------------------------------------')
        round(example_terminator, 'example_rifle', example_terminator_enemy, engagement_details)


multiple_rounds(4)
# TODO check how does the change in ballistic skill change likelihood to land a hit

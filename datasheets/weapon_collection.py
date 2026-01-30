from Weapon import Weapon

# TODO - make 2 different subclasses, ranged weapon and melee weapon
weapon_collection = {
    'example_pistol': Weapon(
        name='example_pistol', weapon_range=12, attacks=6,
        ballistic_skill=4, strength=4, armor_piercing=1, damage=1, keywords={'pistol'}
    ),
    'example_rifle': Weapon(
        name='example_rifle', weapon_range=12, attacks=4,
        ballistic_skill=3, strength=7, armor_piercing=2, damage=2, keywords={'rapid_fire_1'}
    ),
    'example_sword': Weapon(
        name='example_sword', weapon_range=1, attacks=4,
        ballistic_skill=2, strength=4, armor_piercing=3, damage=1, keywords={''}
    ),
    'gaze_of_death': Weapon(
        name='gaze_of_death', weapon_range=18, attacks='D3',
        ballistic_skill=2, strength=12, armor_piercing=3, damage='D6', keywords={''} # TODO - add handling for D6+3 type damage
    ),
    'scythe_of_the_nightbringer_strike': Weapon(
        name='scythe_of_the_nightbringer_strike', weapon_range=1, attacks=6,
        ballistic_skill=2, strength=14, armor_piercing=4, damage='D6', keywords={'devastating_wounds'}
    ),
    'scythe_of_the_nightbringer_sweep': Weapon(
        name='scythe_of_the_nightbringer_sweep', weapon_range=1, attacks=14,
        ballistic_skill=2, strength=8, armor_piercing=2, damage=2, keywords={''}
    ),
    'guardian_spear': Weapon(
        name='guardian_spear', weapon_range=24, attacks=2,
        ballistic_skill=2, strength=4, armor_piercing=1, damage=2, keywords={'assault'}
    )
}

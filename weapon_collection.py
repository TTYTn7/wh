from Weapon import Weapon

weapon_collection = {
    'example_pistol': Weapon(
        name='example_pistol', weapon_range=12, attacks=6,
        ballistic_skill=4, strength=4, armor_piercing=1, damage=1, keywords=['pistol']
    ),
    'example_rifle': Weapon(
        name='example_rifle', weapon_range=12, attacks=4,
        ballistic_skill=3, strength=4, armor_piercing=1, damage=1, keywords=['rapid_fire_1']
    ),
    'example_sword': Weapon(
        name='example_sword', weapon_range=1, attacks=4,
        ballistic_skill=2, strength=4, armor_piercing=3, damage=1, keywords=[]
    )
}

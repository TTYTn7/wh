from Model import Model
from weapon_collection import weapon_collection
from copy import deepcopy

model_collection = {
    'example_terminator_char': Model(
        name='example_terminator_char', movement=5, toughness=4,
        save=2, invulnerable_save=4, wounds=7, leadership=4, objective_control=1,
        ranged_weapons={
            'example_rifle': deepcopy(weapon_collection['example_rifle']),
            'example_pistol': deepcopy(weapon_collection['example_pistol'])
        },
        melee_weapons={'example_sword': deepcopy(weapon_collection['example_sword'])},
        abilities=[], faction=['angels_of_death'],
        keywords={'imperium', 'infantry', 'character', 'terminator'},
        faction_keywords=['adeptus_astartes']
    )
}

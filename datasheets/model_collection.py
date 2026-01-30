from Model import Model
from warhammer.datasheets.weapon_collection import weapon_collection
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
        abilities={}, faction=['angels_of_death'],
        keywords={'imperium', 'infantry', 'character', 'terminator'}, faction_keywords=['adeptus_astartes']
    ),
    'ctan_shard_of_the_nightbringer': Model(
        name='ctan_shard_of_the_nightbringer', movement=10, toughness=11,
        save=3, invulnerable_save=4, wounds=16, leadership=6, objective_control=4,
        ranged_weapons={
            'gaze_of_death': deepcopy(weapon_collection['gaze_of_death'])
        },
        melee_weapons={
            'scythe_of_the_nightbringer_strike ': deepcopy(weapon_collection['scythe_of_the_nightbringer_strike']),
            'scythe_of_the_nightbringer_sweep ': deepcopy(weapon_collection['scythe_of_the_nightbringer_sweep'])
        },
        abilities={'feel_no_pain_5', 'deep_strike', 'deadly_demise_d6'}, faction=['reanimation_protocols'],
        keywords={'monster', 'character', 'epic_hero', 'fly'}, faction_keywords=['necrons']
    ),
    'allarus_custodian': Model(
        name='allarus_custodian', movement=5, toughness=7,
        save=2, invulnerable_save=4, wounds=4, leadership=6, objective_control=2,
        ranged_weapons={
            'guardian_spear': deepcopy(weapon_collection['guardian_spear'])
        },
        melee_weapons={
            'guardian_spear ': deepcopy(weapon_collection['guardian_spear'])
        },
        abilities={'deep_strike'}, faction=['martial_katah'],
        keywords={'infantry', 'terminator', 'imperium'}, faction_keywords=['adeptus_custodes']
    )
}

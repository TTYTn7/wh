from Unit import Unit
from warhammer.datasheets.model_collection import model_collection

unit_collection = {
    'example_terminator_unit': Unit(
        name='example_terminator_unit',
        models=model_collection['example_terminator_char'] * 3,
        point_cost=120,
        in_melee_with=[]
    ),
    'ctan_shard_of_the_nightbringer': Unit(
        name='ctan_shard_of_the_nightbringer',
        models=model_collection['ctan_shard_of_the_nightbringer'] * 1,
        point_cost=315,
        in_melee_with=[]
    ),
    'allarus_custodians': Unit(
        name='allarus_custodians',
        models=model_collection['allarus_custodian'] * 6,
        point_cost=330,
        in_melee_with=[]
    )
}
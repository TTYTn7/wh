from Unit import Unit
from model_collection import model_collection

unit_collection = {
    'example_terminator_unit': Unit(
        name='example_terminator_unit',
        models=model_collection['example_terminator_char'] * 3,
        point_cost=120,
        in_melee_with=[]
    )
}
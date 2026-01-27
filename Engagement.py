from enum import StrEnum
from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Model import Model
    from Unit import Unit


class LastAction(StrEnum):
    remained_stationary = 'remained_stationary'
    advanced = 'advanced'
    charged = 'charged'
    fell_back = 'fell_back'
    disembarked = 'disembarked'
    moved = 'moved'


@dataclass
class Engagement:
    distance: int
    line_of_sight: bool
    # remained_stationary: bool
    # charged: bool
    last_action: LastAction
    in_cover: bool
    engaging_ally: bool
    num_targets: int
    opponent: 'Unit'

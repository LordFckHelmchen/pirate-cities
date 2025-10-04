from collections import namedtuple

from .point2d import Point2d

Range = namedtuple("Range", ["min", "max"])  # noqa: PYI024

INITIAL_SHIP_COUNT_RANGE = Range(1, 3)  # Range of initial ships per city

SCREEN_TITLE = "Pirate Cities"

DAYS_PER_ITERATION = 1  # TODO: Fix all day-based calculations using this constant

SCREEN_SIZE_IN_PX = Point2d(2500, 1000)
UPDATE_RATE_IN_FPS = 30

MAP_SIZE_IN_KM = Point2d(2500, 1000)  # TODO: Only use human
MAP_MARGIN_IN_KM = MAP_SIZE_IN_KM / 25  # Margin around the map for visualization

KM_TO_PX = SCREEN_SIZE_IN_PX / MAP_SIZE_IN_KM
PX_TO_KM = MAP_SIZE_IN_KM / SCREEN_SIZE_IN_PX


### Ships ######################################################################
MIN_SHIP_SPEED_IN_KM_PER_DAY = 1

MOVABLE_CARGO_RANGE_IN_TONS_PER_DAY = Range(10, 50)
"""Tons of cargo that can be moved to/from a ship in a port in a single day"""

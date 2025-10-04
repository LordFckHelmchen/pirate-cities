import math
import random

from .city import CITY_NAMES
from .city import City
from .config import INITIAL_SHIP_COUNT_RANGE
from .config import MAP_MARGIN_IN_KM
from .config import MAP_SIZE_IN_KM
from .point2d import Point2d
from .ship import SHIP_NAMES
from .ship import Ship
from .ship import ShipType


class Simulation:
    def __init__(self, n_cities: int) -> None:
        self.cities = [
            City(name, location)
            for name, location in zip(
                random.sample(CITY_NAMES, n_cities),
                self._generate_city_locations(n_cities),
                strict=False,
            )
        ]

        self.ships = []
        for start_city in self.cities:
            n_ships = random.randint(*INITIAL_SHIP_COUNT_RANGE)  # Randomly decide the number of ships for this city
            # Choose different random destination cities that are not the owner city
            destination_cities = random.sample(
                [dest for dest in self.cities if dest != start_city],
                k=n_ships,
            )
            ship_names = random.sample(SHIP_NAMES, n_ships)  # Randomly select ship names for the ships of this city
            for ship_name, destination_city in zip(ship_names, destination_cities, strict=False):
                ship = Ship(
                    name=ship_name,
                    ship_type=random.choice(list(ShipType)),
                    start=start_city,
                    route=[destination_city],
                    agenda={},
                )
                self.ships.append(ship)

    @staticmethod
    def _generate_city_locations(n_cities: int) -> list[Point2d]:
        """Create n equally spaced city locations on an elipse with the same aspect ratio as the map incorporating margins from the edges."""
        map_size_with_margin_in_km = MAP_SIZE_IN_KM - 2 * MAP_MARGIN_IN_KM
        radius_x = (map_size_with_margin_in_km.x) / 2  # Semi-major axis
        radius_y = (map_size_with_margin_in_km.y) / 2  # Semi-minor axis
        center = map_size_with_margin_in_km / 2 + MAP_MARGIN_IN_KM

        radians_per_city = 2 * math.pi / n_cities

        locations = []
        for i in range(n_cities):
            theta = radians_per_city * i
            x = center.x + radius_x * math.cos(theta)
            y = center.y + radius_y * math.sin(theta)
            locations.append(Point2d(x, y))
        return locations

    def step(self) -> None:
        for ship in self.ships:
            ship.step()
        for city in self.cities:
            city.step()

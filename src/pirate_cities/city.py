import random
from copy import copy
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Self

import numpy as np
import pandas as pd

from pirate_cities.resource import BASE_RESOURCE_PRICE_IN_GOLD
from pirate_cities.resource import RESOURCE_PRICE_ELASTICITY
from pirate_cities.resource import RESOURCE_PRICE_LIMITS

from .config import DAYS_PER_ITERATION
from .config import MAP_SIZE_IN_KM
from .resource import ResourceName

INITIAL_POPULATION_RANGE = (10, 1000)
INITIAL_GOLD_RANGE = (50, 10_000)
INITIAL_FOOD_RANGE = (10, 500)
INITIAL_GOODS_RANGE = (0, 300)
INITIAL_LUXURIES_RANGE = (0, 200)
INITIAL_CANNONS_RANGE = (0, 20)

CITY_INFORMATION_PRICE_IN_GOLD = 100

MIN_SUPPLY_IN_TONS = 1e-5  # Avoid division by zero

INITIAL_CAPACITY = 100
CAPACITY_SCALES = pd.Series(
    {
        "gold": 0.15,
        "food": 0.6,
        "goods": 0.07,
        "luxuries": 0.15,
        "cannons": 0.03,
    },
    name="resource_scaling_factors",
)
CAPACITY_FOOD_IMPACT = 1
GROWTH_RATE_PER_DAY = 0.5


CONSUMPTION_TONS_PER_CAPITA_PER_DAY = pd.Series(
    {
        "gold": 0.0002,
        "food": 0.0063,
        "goods": 0.0025,
        "luxuries": 0.001,
        "cannons": 0.0001,
    },
    name="consumption_per_capita",
)

INITIAL_PRODUCTION_TONS_PER_CAPITA_PER_DAY = pd.Series(
    {
        "gold": 0.0001,
        "food": 0.003,
        "goods": 0.001,
        "luxuries": 0,
        "cannons": 0,
    },
    name="production_per_capita",
)
# INITIAL_PRODUCTION_TONS_PER_CAPITA_PER_DAY *= 1 / INITIAL_PRODUCTION_TONS_PER_CAPITA_PER_DAY.sum()  # Normalize to sum to 1
EXCESS_SUPPLY_FRACTION = 0.8  # Fraction of supply that can be sold as excess

CITY_NAMES = [
    "Baracoa",
    "Barranquilla",
    "Basseterre",
    "Belize City",
    "Bluefields",
    "Bridgetown",
    "Caibarién",
    "Camagüey",
    "Cárdenas",
    "Cartagena",
    "Castries",
    "Charles Town",
    "Charlotte Amalie",
    "Cienfuegos",
    "Cockburn Town",
    "Colón",
    "Consolación del Sur",
    "Cumaná",
    "Florida",
    "Fort-de-France",
    "George Town",
    "Guantánamo",
    "Hamilton",
    "Havana",
    "Holguín",
    "Jatibonico",
    "Kingston",
    "Kingstown",
    "Kralendijk",
    "La Ceiba",
    "La Guaira",
    "Las Tunas",
    "Livingston",
    "Manzanillo",
    "Maracaibo",
    "Matanzas",
    "Morón",
    "Nassau",
    "Nuevitas",
    "Oranjestad",
    "Palma Soriano",
    "Panama City",
    "Philipsburg",
    "Pinar del Río",
    "Pointe-à-Pitre",
    "Ponce",
    "Port of Spain",
    "Port Royal",
    "Port-au-Prince",
    "Providencia",
    "Puerto Barrios",
    "Puerto Cabezas",
    "Puerto Cortés",
    "Puerto La Cruz",
    "Remedios",
    "Riohacha",
    "Road Town",
    "Roseau",
    "San Andrés",
    "San Juan",
    "San Pedro Sula",
    "Santa Clara",
    "Santa Marta",
    "Santiago de Cuba",
    "Santo Domingo",
    "Scarborough",
    "St. George's",
    "St. John's",
    "The Valley",
    "Tortuga",
    "Trinidad",
    "Victoria de Las Tunas",
    "Willemstad",
]


@dataclass
class City:
    name: str
    location: tuple[float, float] = field(
        default_factory=lambda: (
            random.uniform(0, MAP_SIZE_IN_KM[0]),
            random.uniform(0, MAP_SIZE_IN_KM[1]),
        ),
    )

    base_population: int = field(
        default_factory=lambda: random.randint(*INITIAL_POPULATION_RANGE),
    )

    gold: int = field(default_factory=lambda: random.randint(*INITIAL_GOLD_RANGE))
    food: int = field(default_factory=lambda: random.randint(*INITIAL_FOOD_RANGE))
    goods: int = field(default_factory=lambda: random.randint(*INITIAL_GOODS_RANGE))
    luxuries: int = field(
        default_factory=lambda: random.randint(*INITIAL_LUXURIES_RANGE),
    )
    cannons: int = field(default_factory=lambda: random.randint(*INITIAL_CANNONS_RANGE))

    recency_in_iterations: int = 0

    information: dict[str, Self] = field(default_factory=dict)

    _cache: dict[str, Any] = field(default_factory=dict)

    @property
    def base_capacity(self) -> float:
        """Compute the base capacity of the city based on its resources."""
        return self._cache.get(
            "base_capacity",
            INITIAL_CAPACITY / (1 + 10 ** (-self.food / 1_000)),
        )  # Food has a strong impact on capacity

    @property
    def capacity(self) -> float:
        """Compute the capacity of the city based on its resources."""
        return self._cache.get(
            "capacity",
            self.base_capacity
            * (1 + sum(self[resource] * CAPACITY_SCALES[resource] for resource in CAPACITY_SCALES.index)),
        )

    @property
    def population(self) -> int:
        """Get the population of the city."""
        return self._cache.get(
            "population",
            self.capacity
            / (1 + (self.capacity / self.base_population - 1) * np.exp(-GROWTH_RATE_PER_DAY * DAYS_PER_ITERATION)),
        )

    def freeze(self) -> None:
        """Cache the values of base_capacity, capacity, and population."""
        self._cache = {
            "base_capacity": self.base_capacity,
            "capacity": self.capacity,
            "population": self.population,
        }

    def unfreeze(self) -> None:
        """Clear the cache."""
        self._cache = {}

    def demand(self, resource: ResourceName) -> float:
        """Compute the demand of the city based on its population."""
        return self.population * CONSUMPTION_TONS_PER_CAPITA_PER_DAY[resource]

    def supply(self, resource: ResourceName) -> float:
        """Return the supply of the city based of a given resource."""
        return self[resource]

    def excess_supply(self, resource: ResourceName) -> float:
        """Compute the excess supply of the city based on its population."""
        return max(
            0,
            EXCESS_SUPPLY_FRACTION * (self.supply(resource) - self.demand(resource)),
        )

    def production(self, resource: ResourceName) -> float:
        """Compute the production of the city based on its population."""
        return self.population * INITIAL_PRODUCTION_TONS_PER_CAPITA_PER_DAY[resource]

    def price(self, resource: ResourceName) -> float:
        if self.demand(resource) <= 0:
            return RESOURCE_PRICE_LIMITS[0]  # No demand, price at lower limit
        if self.supply(resource) <= 0:
            return RESOURCE_PRICE_LIMITS[1]  # No supply, price at upper limit
        return np.clip(
            BASE_RESOURCE_PRICE_IN_GOLD[resource]
            * (self.demand(resource) / self.supply(resource)) ** RESOURCE_PRICE_ELASTICITY,
            *RESOURCE_PRICE_LIMITS,
        )

    def __getitem__(self, item: str) -> int:
        """Get the value of an attribute."""
        return self.__dict__[item]

    def __setitem__(self, item: str, value: Any) -> None:
        """Set the value of an attribute."""
        self.__dict__[item] = value

    def step(self) -> None:
        """Perform a step in the simulation."""
        self.freeze()

        # Consume & produce resources
        for resource in ResourceName:
            resource_diff = self.production(resource) - self.demand(resource)
            self[resource] = self.supply(resource) + resource_diff
            # if resource_diff < 0:
            #     # If demand is greater than supply, we need to buy resources
            #     cost = min(-resource_diff * self.price(resource), self.gold)
            #     print(
            #         # f"City {self.name} buys {cost / self.price(resource)} tons of {resource} for {cost} gold"
            #     )
            #     self.gold -= cost
            #     self[resource] += cost / self.price(resource)
            # else:
            #     # If supply is greater than demand, we need to sell resources
            #     resource_diff = self.excess_supply(resource)
            #     revenue = resource_diff * self.price(resource)
            #     print(
            #         # f"City {self.name} sells {resource_diff} tons of {resource} for {revenue} gold"
            #     )
            #     self.gold += revenue
            #     self[resource] -= resource_diff

        # Reproduce
        self.base_population *= (1 + GROWTH_RATE_PER_DAY * (1 - self.population / self.capacity)) * DAYS_PER_ITERATION

        self.unfreeze()
        self.recency_in_iterations += 1

    def buy_city_info(self, source_city: Self) -> float:
        """
        Update the city information with the given information.

        Only buy information that is unknown or newer than the existing one.
        Prefer to buy information for which the city's information is most outdated.
        """

        # Assure that the source city is also included in the information.
        city_infos = {source_city.name: source_city} | source_city.information

        # Determine which city information is newer than the existing one.
        city_info_recency_diff = {}
        for city in city_infos.values():
            if city.name not in self.information:
                city_info_recency_diff[city.name] = np.inf
            elif (recency_diff := city.recency_in_iterations - self.information[city.name].recency_in_iterations) > 0:
                # Only consider cities with newer information
                city_info_recency_diff[city.name] = recency_diff

        # Sort by recency; most outdated first
        city_info_recency_diff = sorted(
            city_info_recency_diff.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        price_in_gold = 0.0
        for city_name, _ in city_info_recency_diff:
            if self.gold < CITY_INFORMATION_PRICE_IN_GOLD:
                break
            self.information[city_name] = copy(city_infos[city_name])
            price_in_gold += CITY_INFORMATION_PRICE_IN_GOLD
            self.gold -= CITY_INFORMATION_PRICE_IN_GOLD

        return price_in_gold

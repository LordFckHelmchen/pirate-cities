import logging
import random
from collections.abc import Generator
from copy import copy
from dataclasses import dataclass
from enum import Enum
from enum import IntEnum
from typing import Self

import numpy as np

from .city import City
from .resource import ResourceName

# French Heritage
FRENCH_SHIP_NAMES = [
    "Le Vengeur",
    "La Sirène",
    "Le Dragon",
    "La Belle Étoile",
    "Le Corsaire",
    "La Perle Noire",
    "Le Fantôme",
    "La Fleur de Mer",
    "Le Tigre",
    "La Reine des Mers",
    "Le Vent Rapide",
    "La Licorne",
    "Le Soleil Levant",
    "La Tempête",
    "Le Dauphin",
    "La Fortune",
    "Le Lion d'Or",
    "La Victoire",
    "Le Phénix",
    "La Liberté",
]
# Dutch Heritage
DUTCH_SHIP_NAMES = [
    "De Vliegende Hollander",
    "De Gouden Leeuw",
    "De Zeemeeuw",
    "De Dappere Zeeman",
    "De Stormvogel",
    "De Zilveren Maan",
    "De Rode Draak",
    "De Vrijheid",
    "De Zeeslang",
    "De Noorderwind",
    "De Blauwe Golven",
    "De Drie Gebroeders",
    "De Ster van de Zee",
    "De Vurige Haas",
    "De Zwarte Roos",
    "De Eendracht",
    "De Gouden Zon",
    "De Zeehond",
    "De Vliegende Vis",
    "De Trots van Holland",
]
# Spanish Heritage
SPANISH_SHIP_NAMES = [
    "El León de Oro",
    "La Santa María",
    "El Dragón de Fuego",
    "La Estrella del Mar",
    "El Corsario Negro",
    "La Perla Negra",
    "El Rayo Veloz",
    "La Fortuna",
    "El Águila Real",
    "La Sirena del Caribe",
    "El Tesoro Perdido",
    "La Victoria",
    "El Halcón del Mar",
    "La Luna Nueva",
    "El Tigre Feroz",
    "La Dama del Mar",
    "El Sol Brillante",
    "La Tormenta",
    "El Barco Fantasma",
    "La Libertad",
]
# English Heritage
ENGLISH_SHIP_NAMES = [
    "The Black Pearl",
    "The Royal Fortune",
    "The Queen Anne's Revenge",
    "The Adventure Galley",
    "The Fancy",
    "The Whydah",
    "The Golden Hind",
    "The Revenge",
    "The Victory",
    "The Defiant",
    "The Swift",
    "The Resolution",
    "The Endeavour",
    "The Discovery",
    "The Triumph",
    "The Sovereign",
    "The Merlin",
    "The Phoenix",
    "The Liberty",
    "The Sea Hawk",
]
SHIP_NAMES = FRENCH_SHIP_NAMES + DUTCH_SHIP_NAMES + SPANISH_SHIP_NAMES + ENGLISH_SHIP_NAMES


class ShipSpeed(IntEnum):
    """Speed of the ship in km per iteration."""

    VERY_SLOW = 100
    SLOW = 200
    MODERATE = 300
    FAST = 400
    VERY_FAST = 500


class ShipType(Enum):
    # Pinnace class
    WAR_CANOE = "War Canoe"
    PINNACE = "Pinnace"
    MAIL_RUNNER = "Mail Runner"

    # Sloop class
    SLOOP = "Sloop"
    SLOOP_OF_WAR = "Sloop of War"
    ROYAL_SLOOP = "Royal Sloop"

    # Brig class
    BRIGANTINE = "Brigantine"
    BRIG = "Brig"
    BRIG_OF_WAR = "Brig of War"

    # Barque class
    COASTAL_BARQUE = "Coastal Barque"
    BARQUE = "Barque"
    OCEAN_BARQUE = "Ocean Barque"

    # Fluyt class
    FLUYT = "Fluyt"
    LARGE_FLUYT = "Large Fluyt"
    WEST_INDIANMAN = "West Indianman"

    # Merchantman class
    MERCHANTMAN = "Merchantman"
    LARGE_MERCHANTMAN = "Large Merchantman"
    EAST_INDIANMAN = "East Indianman"

    # Galleon class
    FAST_GALLEON = "Fast Galleon"
    WAR_GALLEON = "War Galleon"
    FLAG_GALLEON = "Flag Galleon"

    # Frigate class
    FRIGATE = "Frigate"
    LARGE_FRIGATE = "Large Frigate"
    SHIP_OF_THE_LINE = "Ship of the Line"


@dataclass(frozen=True)
class ShipSpec:
    type: ShipType
    speed: ShipSpeed
    max_cargo_hold_in_tons: float
    max_cannons: int

    @classmethod
    def from_type(cls, ship_type: ShipType) -> Self:  # noqa: C901, PLR0911, PLR0912  # Not complex, just a match-case
        match ship_type:
            case ShipType.WAR_CANOE:
                return cls(type=ship_type, speed=ShipSpeed.VERY_FAST, max_cargo_hold_in_tons=20, max_cannons=8)
            case ShipType.PINNACE:
                return cls(type=ship_type, speed=ShipSpeed.VERY_FAST, max_cargo_hold_in_tons=25, max_cannons=10)
            case ShipType.MAIL_RUNNER:
                return cls(type=ship_type, speed=ShipSpeed.VERY_FAST, max_cargo_hold_in_tons=30, max_cannons=12)
            case ShipType.SLOOP:
                return cls(type=ship_type, speed=ShipSpeed.FAST, max_cargo_hold_in_tons=40, max_cannons=12)
            case ShipType.SLOOP_OF_WAR:
                return cls(type=ship_type, speed=ShipSpeed.FAST, max_cargo_hold_in_tons=50, max_cannons=16)
            case ShipType.ROYAL_SLOOP:
                return cls(type=ship_type, speed=ShipSpeed.FAST, max_cargo_hold_in_tons=60, max_cannons=20)
            case ShipType.BRIGANTINE:
                return cls(type=ship_type, speed=ShipSpeed.MODERATE, max_cargo_hold_in_tons=60, max_cannons=20)
            case ShipType.BRIG:
                return cls(type=ship_type, speed=ShipSpeed.MODERATE, max_cargo_hold_in_tons=80, max_cannons=24)
            case ShipType.BRIG_OF_WAR:
                return cls(type=ship_type, speed=ShipSpeed.MODERATE, max_cargo_hold_in_tons=80, max_cannons=32)
            case ShipType.COASTAL_BARQUE:
                return cls(type=ship_type, speed=ShipSpeed.SLOW, max_cargo_hold_in_tons=60, max_cannons=12)
            case ShipType.BARQUE:
                return cls(type=ship_type, speed=ShipSpeed.SLOW, max_cargo_hold_in_tons=70, max_cannons=16)
            case ShipType.OCEAN_BARQUE:
                return cls(type=ship_type, speed=ShipSpeed.SLOW, max_cargo_hold_in_tons=80, max_cannons=16)
            case ShipType.FLUYT:
                return cls(type=ship_type, speed=ShipSpeed.VERY_SLOW, max_cargo_hold_in_tons=80, max_cannons=8)
            case ShipType.LARGE_FLUYT:
                return cls(type=ship_type, speed=ShipSpeed.VERY_SLOW, max_cargo_hold_in_tons=100, max_cannons=12)
            case ShipType.WEST_INDIANMAN:
                return cls(type=ship_type, speed=ShipSpeed.VERY_SLOW, max_cargo_hold_in_tons=120, max_cannons=16)
            case ShipType.MERCHANTMAN:
                return cls(type=ship_type, speed=ShipSpeed.SLOW, max_cargo_hold_in_tons=100, max_cannons=16)
            case ShipType.LARGE_MERCHANTMAN:
                return cls(type=ship_type, speed=ShipSpeed.SLOW, max_cargo_hold_in_tons=120, max_cannons=20)
            case ShipType.EAST_INDIANMAN:
                return cls(type=ship_type, speed=ShipSpeed.SLOW, max_cargo_hold_in_tons=140, max_cannons=20)
            case ShipType.FAST_GALLEON:
                return cls(type=ship_type, speed=ShipSpeed.SLOW, max_cargo_hold_in_tons=80, max_cannons=24)
            case ShipType.WAR_GALLEON:
                return cls(type=ship_type, speed=ShipSpeed.SLOW, max_cargo_hold_in_tons=90, max_cannons=32)
            case ShipType.FLAG_GALLEON:
                return cls(type=ship_type, speed=ShipSpeed.SLOW, max_cargo_hold_in_tons=100, max_cannons=40)
            case ShipType.FRIGATE:
                return cls(type=ship_type, speed=ShipSpeed.FAST, max_cargo_hold_in_tons=80, max_cannons=32)
            case ShipType.LARGE_FRIGATE:
                return cls(type=ship_type, speed=ShipSpeed.FAST, max_cargo_hold_in_tons=90, max_cannons=40)
            case ShipType.SHIP_OF_THE_LINE:
                return cls(type=ship_type, speed=ShipSpeed.FAST, max_cargo_hold_in_tons=100, max_cannons=48)
            case _:
                msg = f"Unknown ship type: {ship_type}"
                raise ValueError(msg)


class Ship:
    def __init__(
        self,
        name: str,
        start: City,
        destination: City,
        ship_type: ShipType,
    ) -> None:
        self.name = name
        self._ship_spec = ShipSpec.from_type(ship_type)

        # Set by according properties/functions
        self._destination = destination
        self._has_arrived = False
        self.cargo = dict.fromkeys(ResourceName, 0)
        self.gold = 0

        self.start = start

        self.clear_cargo()
        self.depart(destination)

    @property
    def ship_spec(self) -> ShipSpec:
        """Get the spec of the ship."""
        return self._ship_spec

    @property
    def destination(self) -> City:
        return self._destination

    @property
    def iterations_en_route(self) -> int:
        return self._iterations_en_route

    def set_new_destination(self, new_destination: City) -> None:
        """Set a new destination for the ship and mark it as not having arrived."""
        self._destination = new_destination
        self._has_arrived = False
        self._iterations_en_route = 0

    def clear_cargo(self) -> None:
        """Clear the cargo of the ship."""
        self.cargo = dict.fromkeys(ResourceName, 0)
        self.gold = 0

    def depart(self, destination: City) -> None:
        self.set_new_destination(destination)
        # TODO: Use the information from the current location to set the info
        self.destination_info = copy(self.destination)
        self.owner_info = copy(self.start)

        # Record prices, population, and fill cargo with what owner city wants to sell
        self.load_cargo_to_sell()

        self.location = copy(self.start.location)

    @property
    def has_arrived(self) -> bool:
        """Check if the ship has arrived at its destination."""
        return self._has_arrived

    def travel(self) -> None:
        """Travel one iteration towards the destination city."""
        # Calculate the distance to the destination
        self._iterations_en_route += 1
        dest_loc = np.array(self.destination.location)
        self_loc = np.array(self.location)
        if (
            distance := np.linalg.norm(dest_loc - self_loc)
        ) > self._ship_spec.speed:  # Check if we can't reach the destination in this iteration
            # Move towards the destination
            direction = (dest_loc - self_loc) / distance
            self_loc += direction * self._ship_spec.speed
            self.location = tuple(self_loc)
        else:
            self._has_arrived = True
            # If the ship is close enough, it arrives at the destination, sells any cargo for the price at the
            # destination, loads the gold and travels back to the start City to hand over the gold.
            self.location = self.destination.location
            if self.location == self.start.location:
                self.arrive_home()
            else:
                self.arrive_at_destination()

    def get_resource_names_ordered_by_margin(self) -> Generator[ResourceName]:
        """Sort resources by the margin between the current destination and past owner prices & return highest first."""
        margins = {}
        for resource in ResourceName:
            margins[resource] = self.destination.price(
                resource,
            ) - self.owner_info.price(resource)

        yield from sorted(margins, key=margins.get, reverse=True)  # Highest first

    @property
    def loaded_cargo_in_tons(self) -> float:
        """Calculate the total cargo loaded in tons."""
        return sum(self.cargo.values())

    def load_cargo_to_sell(self) -> None:
        # Decide what and how much to sell (e.g., excess resources)
        excesses = {resource: self.start.excess_supply(resource) for resource in ResourceName}
        # TODO: Load cargo with highest margin at destination first
        for resource, excess_supply_in_tons in sorted(
            excesses.items(),
            key=lambda x: x[1],
            reverse=True,
        ):  # Sort by excess supply; highest first
            remaining_cargo_hold_in_tons = self._ship_spec.max_cargo_hold_in_tons - self.loaded_cargo_in_tons
            if remaining_cargo_hold_in_tons <= 0 or excess_supply_in_tons <= 0:
                break

            self.cargo[resource] = int(
                min(excess_supply_in_tons, remaining_cargo_hold_in_tons),
            )
            self.start[resource] -= self.cargo[resource]

        self.gold = int(0.3 * random.random() * self.start.gold)
        self.start.gold -= self.gold

    @property
    def cargo_to_buy(self) -> Generator[tuple[ResourceName, float]]:
        # Decide what and how much to buy (e.g., resources in demand)
        demands = {
            resource: int(self.owner_info.demand(resource))
            for resource in ResourceName
            if self.owner_info.demand(resource) > 0
        }

        # Sort by demand; highest first & filter out zero demands
        yield from sorted(demands.items(), key=lambda x: x[1], reverse=True)

    def sell_cargo_at_destination(self) -> None:
        """Sell cargo at destination with the best margin first."""
        for resource in self.get_resource_names_ordered_by_margin():
            price_in_gold_per_ton = self.destination.price(
                resource,
            )  # Current price at destination
            earnings_in_gold = min(
                self.cargo[resource] * price_in_gold_per_ton,
                self.destination.gold,
            )
            cargo_sold_in_tons = int(earnings_in_gold / price_in_gold_per_ton)
            earnings_in_gold = cargo_sold_in_tons * price_in_gold_per_ton
            self.cargo[resource] -= cargo_sold_in_tons
            self.destination[resource] += cargo_sold_in_tons
            self.gold += earnings_in_gold
            self.destination.gold -= earnings_in_gold

    def buy_cargo_at_destination(self) -> None:
        """Buy cargo at destination with the best margin first."""
        for resource, amount_in_tons in self.cargo_to_buy:
            remaining_cargo_hold_in_tons = self._ship_spec.max_cargo_hold_in_tons - self.loaded_cargo_in_tons
            if remaining_cargo_hold_in_tons <= 0:
                logging.getLogger(__name__).debug(f"Ship {self.name} cannot buy more cargo: full.")
                break
            if self.gold <= 0:
                logging.getLogger(__name__).debug(f"Ship {self.name} cannot buy more cargo, out of gold.")
                break

            price_in_gold_per_ton = self.destination.price(
                resource,
            )  # Current price at destination
            max_price_for_sale_in_gold = (
                min(amount_in_tons, self.destination.excess_supply(resource)) * price_in_gold_per_ton
            )
            amount_to_buy_in_tons = int(
                min(
                    remaining_cargo_hold_in_tons,
                    min(self.gold, max_price_for_sale_in_gold) / price_in_gold_per_ton,
                ),
            )
            self.cargo[resource] += amount_to_buy_in_tons
            self.gold -= amount_to_buy_in_tons * price_in_gold_per_ton

    def arrive_home(self) -> None:
        """Handle the arrival of the ship back at its home city."""
        self.start.gold += self.gold
        for resource in ResourceName:
            self.start[resource] += self.cargo[resource]
        self.clear_cargo()

        # Nothing to pay for - we are the owner.
        paid_information_price_in_gold = self.start.buy_city_info(self.destination_info)
        self.start.gold += paid_information_price_in_gold

    def arrive_at_destination(self) -> None:
        """Handle the arrival of the ship at its destination city."""
        self.sell_cargo_at_destination()

        # Buy cargo at destination with the best margin first
        self.buy_cargo_at_destination()

        # Update destination's price info with what ship observed at departure and earn some gold for it
        self.gold += self.destination.buy_city_info(self.owner_info)

        # Set up for return trip
        self.destination_info = copy(self.destination)
        self._destination = self.start  # Return to owner city

    def as_string(self) -> str:
        return (
            f"{self.name} ({self.ship_spec.type.value}) from {self.start.name} to {self.destination.name}, "
            f"carrying {', '.join(f'{amount}t {name.value}' for name, amount in self.cargo.items())} "
            f"and {self.gold} gold."
        )

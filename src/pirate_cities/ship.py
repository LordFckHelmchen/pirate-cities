import logging
import math
import random
from collections.abc import Generator
from copy import copy
from dataclasses import dataclass
from enum import Enum
from enum import IntEnum
from typing import Self

from .city import City
from .config import MIN_SHIP_SPEED_IN_KM_PER_DAY
from .config import MOVABLE_CARGO_RANGE_IN_TONS_PER_DAY
from .point2d import Point2d
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

    VERY_SLOW = MIN_SHIP_SPEED_IN_KM_PER_DAY
    SLOW = 2 * MIN_SHIP_SPEED_IN_KM_PER_DAY
    MODERATE = 3 * MIN_SHIP_SPEED_IN_KM_PER_DAY
    FAST = 4 * MIN_SHIP_SPEED_IN_KM_PER_DAY
    VERY_FAST = 5 * MIN_SHIP_SPEED_IN_KM_PER_DAY


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


class ShipState(Enum):
    AT_SEA = "At Sea"
    ARRIVED_AT_PORT = "Arrived at Port"
    WAITING_FOR_DEPARTURE = "Waiting for Departure"


class Ship:
    def __init__(
        self,
        name: str,
        ship_type: ShipType,
        start: City,
        route: list[City],
        agenda: dict[str, dict] | None = None,
    ) -> None:
        self.name = name
        self._ship_spec = ShipSpec.from_type(ship_type)

        self._sold_cargo: dict[ResourceName, int] = None
        self._cargo: dict[ResourceName, int] = None
        self._gold = None
        self.clear_cargo()

        self._start = start
        self._route: list[City] = None
        self._agenda: dict[str, dict] = None
        self._current_stop_index = None
        self.set_itinerary(start, route, agenda)

        self._location = copy(start.location)
        self._state = ShipState.WAITING_FOR_DEPARTURE
        self._waiting_iterations_remaining = 0

        # Do not automatically depart on construction; allow tests and callers to control first departure

    @property
    def ship_spec(self) -> ShipSpec:
        """Get the spec of the ship."""
        return self._ship_spec

    @property
    def destination(self) -> City:
        return self._destination

    @property
    def current_location(self) -> Point2d:
        return self._location

    @property
    def iterations_en_route(self) -> int:
        return self._iterations_en_route

    def set_itinerary(self, start: City, route: list[City], agenda: dict[str, dict]) -> None:
        """Set a multi-stop route (excluding home) and an optional agenda per city.

        Example agenda: {"Port Royal": {"sell": {ResourceName.FOOD: None}, "buy": {ResourceName.GOODS: 10}}}
        """
        self._route = route
        if route[-1] != start:
            self._route.append(start)  # Ensure we return home at end of route
        self._agenda = agenda
        self._current_stop_index = 0

        # Initialize next destination so the ship has a valid destination before first depart
        self._destination = self._route[self._current_stop_index]

    def clear_cargo(self) -> None:
        """Clear the cargo of the ship."""
        self._sold_cargo = dict.fromkeys(ResourceName, 0)
        self._cargo = dict.fromkeys(ResourceName, 0)
        self._gold = 0

    def _depart(self) -> None:
        # If currently on the way do nothing.
        if self._state != ShipState.WAITING_FOR_DEPARTURE:
            return

        # If currently waiting at a port, do not depart until waiting is done
        if self._waiting_iterations_remaining > 0:
            self._waiting_iterations_remaining -= 1
            return

        # Pick next stop
        self._destination = self._route[self._current_stop_index] if self._route else self._start
        self._state = ShipState.AT_SEA
        self._iterations_en_route = 0

        # Update cached info snapshots
        self.destination_info = copy(self.destination)
        self.owner_info = copy(self._start)

        # Load initial cargo to sell based on owner's excess supply
        self._load_cargo_to_sell()

    # Do not forcibly reset the ship's location here; it should continue from current position

    @property
    def has_arrived(self) -> bool:
        """Check if the ship has arrived at its destination."""
        return self._state == ShipState.ARRIVED_AT_PORT

    def _travel(self) -> None:
        """Travel one iteration towards the destination city."""
        if self._state != ShipState.AT_SEA:
            return

        self._iterations_en_route += 1

        # Calculate the distance to the destination
        dest_loc = self.destination.location
        if (
            distance := self._location.distance_to(dest_loc)
        ) > self._ship_spec.speed:  # Check if we can't reach the destination in this iteration
            # Move towards the destination
            direction = dest_loc - self._location
            self._location += direction * (self._ship_spec.speed / distance)
        else:  # Close enough to destination
            # Copy the city's location so the ship does not hold a reference to the same Point2d
            self._location = copy(self.destination.location)
            # The ship arrives at the destination
            self._state = ShipState.ARRIVED_AT_PORT

    def get_resource_names_ordered_by_margin(self) -> Generator[ResourceName]:
        """Sort resources by the margin between the current destination and past owner prices & return highest first."""
        margins = {}
        for resource in ResourceName:
            margins[resource] = self.destination.price(
                resource,
            ) - self.owner_info.price(resource)

        yield from sorted(margins, key=margins.get, reverse=True)  # Highest first

    @property
    def total_cargo_in_tons(self) -> float:
        """Calculate the total cargo loaded in tons."""
        return sum(self._cargo.values())

    def _load_cargo_to_sell(self) -> None:
        # Decide what and how much to sell (e.g., excess resources)
        excesses = {resource: self._start.excess_supply(resource) for resource in ResourceName}
        # TODO: Load cargo with highest margin at destination first
        for resource, excess_supply_in_tons in sorted(
            excesses.items(),
            key=lambda x: x[1],
            reverse=True,
        ):  # Sort by excess supply; highest first
            remaining_cargo_hold_in_tons = self._ship_spec.max_cargo_hold_in_tons - self.total_cargo_in_tons
            if remaining_cargo_hold_in_tons <= 0 or excess_supply_in_tons <= 0:
                break

            self._cargo[resource] = int(
                min(excess_supply_in_tons, remaining_cargo_hold_in_tons),
            )
            self._start[resource] -= self._cargo[resource]

        self._gold = int(0.3 * random.random() * self._start.gold)
        self._start.gold -= self._gold

    def _handle_arrival(self) -> None:
        """Process arrival at the current destination: update info, perform agenda sell/buy and set next destination."""
        if self._state != ShipState.ARRIVED_AT_PORT:
            return

        # Update snapshot information
        self.destination_info = copy(self.destination)
        self.owner_info = copy(self._start)

        # If arrived home, process return
        if self._location == self._start.location:
            self._arrive_home()
            # no further route required
            self._waiting_iterations_remaining = 0
            return

        # Process sells/buys according to agenda for this city
        city_name = self.destination.name

        # Snapshot cargo before actions to compute moved tons
        cargo_before = copy(self._cargo)

        self._sold_cargo = dict.fromkeys(ResourceName, 0)
        # Sell per agenda; if no agenda provided, fall back to existing behavior
        if city_name in self._agenda and "sell" in self._agenda[city_name]:
            self._sell_per_agenda(city_name)
        else:
            # default: sell based on margins
            self._sell_cargo_at_destination()

        # Buy per agenda (only if agenda instructs buying at this city)
        if city_name in self._agenda and "buy" in self._agenda[city_name]:
            self._buy_per_agenda(city_name)
        else:
            # Default: opportunistic buying based on owner's demand
            self._buy_cargo_at_destination()

        # The destination may pay for info
        self._gold += self.destination.buy_city_info(self.owner_info)

        # Snapshot cargo after actions and compute moved tons (sold + bought)
        total_cargo_moved_in_tons = sum(abs(self._cargo[r] - cargo_before[r]) for r in ResourceName)

        # Get random waiting time based on movable cargo range per day
        movable_cargo_in_tons_per_day = random.uniform(*MOVABLE_CARGO_RANGE_IN_TONS_PER_DAY)
        # Wait at least 1 day if cargo was moved
        self._waiting_iterations_remaining = math.ceil(total_cargo_moved_in_tons / movable_cargo_in_tons_per_day)
        self._state = ShipState.WAITING_FOR_DEPARTURE

        # Set next destination: advance in route or return home
        if self._current_stop_index < len(self._route):
            # move to next stop index (we just arrived at route[_current_stop_index])
            self._current_stop_index += 1
        # determine the next city to go to (if any left, otherwise return home)
        if self._current_stop_index < len(self._route):
            self._destination = self._route[self._current_stop_index]
        else:
            self._destination = self._start

    def _sell_per_agenda(self, city_name: str) -> None:
        """Sell resources at this city according to the owner's agenda."""
        orders = self._agenda.get(city_name, {}).get("sell", {})
        for resource, amount in orders.items():
            available = self._cargo.get(resource, 0)
            if available <= 0:
                continue
            to_sell = available if amount is None else int(min(available, amount))
            price = self.destination.price(resource)
            earnings = to_sell * price
            # perform sale limited by city gold
            actual_earnings = min(earnings, self.destination.gold)
            actual_sold = int(actual_earnings / price) if price > 0 else 0
            self._cargo[resource] -= actual_sold
            self.destination[resource] += actual_sold
            self._gold += actual_sold * price
            self.destination.gold -= actual_sold * price
            self._sold_cargo[resource] = actual_sold

    def _buy_per_agenda(self, city_name: str) -> None:
        """Buy resources at this city according to agenda, preferring to buy here if price is cheapest among remaining stops."""
        orders = self._agenda.get(city_name, {}).get("buy", {})
        # Determine remaining stops (this city included and future route stops)
        remaining_cities = [self.destination, *self._route[self._current_stop_index + 1 :]]
        for resource, target_amount in orders.items():
            # how much already on board
            already = self._cargo.get(resource, 0)
            need = float("inf") if target_amount is None else max(0, int(target_amount) - already)
            if need <= 0:
                continue
            # compute cheapest future price among remaining_cities
            future_prices = [c.price(resource) for c in remaining_cities if c is not None]
            min_future_price = min(future_prices) if future_prices else self.destination.price(resource)
            current_price = self.destination.price(resource)
            # If current city is cheapest (ties included), buy here up to need, capacity, gold, and supplier
            if current_price <= min_future_price:
                remaining_capacity = int(self._ship_spec.max_cargo_hold_in_tons - self.total_cargo_in_tons)
                if remaining_capacity <= 0:
                    break
                supplier = self.destination.excess_supply(resource)
                amount_available = int(
                    min(need if need != float("inf") else remaining_capacity, supplier, remaining_capacity),
                )
                max_affordable = int(self._gold // current_price) if current_price > 0 else 0
                buy_amount = int(min(amount_available, max_affordable))
                if buy_amount <= 0:
                    continue
                self._cargo[resource] += buy_amount
                self._gold -= buy_amount * current_price
                self.destination[resource] -= buy_amount

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

    def _sell_cargo_at_destination(self) -> None:
        """Sell cargo at destination with the best margin first."""
        for resource in self.get_resource_names_ordered_by_margin():
            price_in_gold_per_ton = self.destination.price(
                resource,
            )  # Current price at destination
            earnings_in_gold = min(
                self._cargo[resource] * price_in_gold_per_ton,
                self.destination.gold,
            )
            cargo_sold_in_tons = int(earnings_in_gold / price_in_gold_per_ton)
            earnings_in_gold = cargo_sold_in_tons * price_in_gold_per_ton
            self._cargo[resource] -= cargo_sold_in_tons
            self.destination[resource] += cargo_sold_in_tons
            self._gold += earnings_in_gold
            self.destination.gold -= earnings_in_gold

    def _buy_cargo_at_destination(self) -> None:
        """Buy cargo at destination with the best margin first."""
        for resource, amount_in_tons in self.cargo_to_buy:
            remaining_cargo_hold_in_tons = self._ship_spec.max_cargo_hold_in_tons - self.total_cargo_in_tons
            if remaining_cargo_hold_in_tons <= 0:
                logging.getLogger(__name__).debug(f"Ship {self.name} cannot buy more cargo: full.")
                break
            if self._gold <= 0:
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
                    min(self._gold, max_price_for_sale_in_gold) / price_in_gold_per_ton,
                ),
            )
            self._cargo[resource] += amount_to_buy_in_tons
            self._gold -= amount_to_buy_in_tons * price_in_gold_per_ton

    def _arrive_home(self) -> None:
        """Handle the arrival of the ship back at its home city."""
        self._start.gold += self._gold
        for resource in ResourceName:
            self._start[resource] += self._cargo[resource]
        self.clear_cargo()

        # Nothing to pay for - we are the owner.
        paid_information_price_in_gold = self._start.buy_city_info(self.destination_info)
        self._start.gold += paid_information_price_in_gold

    def _arrive_at_destination(self) -> None:
        """Handle the arrival of the ship at its destination city."""
        self._sell_cargo_at_destination()

        # Buy cargo at destination with the best margin first
        self._buy_cargo_at_destination()

        # Update destination's price info with what ship observed at departure and earn some gold for it
        self._gold += self.destination.buy_city_info(self.owner_info)

        # Set up for return trip
        self.destination_info = copy(self.destination)
        self._destination = self._start  # Return to owner city

    def as_string(self) -> str:
        return (
            f"{self.name} ({self.ship_spec.type.value}) from {self._start.name} to {self.destination.name}, "
            f"carrying {', '.join(f'{amount}t {name.value}' for name, amount in self._cargo.items())} "
            f"and {self._gold} gold."
        )

    def step(self) -> None:
        """Advance the ship's state by one iteration."""
        self._travel()
        self._handle_arrival()
        self._depart()

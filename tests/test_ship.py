import copy
from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from pirate_cities.city import CITY_INFORMATION_PRICE_IN_GOLD
from pirate_cities.city import City
from pirate_cities.resource import ResourceName
from pirate_cities.ship import Ship
from pirate_cities.ship import ShipSpec
from pirate_cities.ship import ShipType


@pytest.fixture
def ship() -> Ship:
    owner_city = City("OwnerCity", location=(0.0, 0.0))
    initial_destination_city = City("InitialDestinationCity", location=(100.0, 0.0))
    return Ship(
        name="TestShip",
        start=owner_city,
        destination=initial_destination_city,
        ship_type=ShipType.SLOOP,
    )


def test_initialization_sets_destination_and_departs_with_cargo() -> None:
    owner_city = City("OwnerCity", location=(0.0, 0.0))
    initial_destination_city = City("InitialDestinationCity", location=(100.0, 0.0))
    expected_ship_spec = ShipSpec.from_type(ShipType.BARQUE)
    ship = Ship(
        name="TestShip",
        start=owner_city,
        destination=initial_destination_city,
        ship_type=expected_ship_spec.type,
    )

    assert ship.name == "TestShip"

    assert ship.start == owner_city
    assert id(ship.owner_info) != id(owner_city), (
        f"Owner info (id={id(ship.owner_info)}) should be a copy of the owner city (id={id(owner_city)})"
    )
    assert ship.owner_info.name == owner_city.name

    assert ship.destination == initial_destination_city
    assert id(ship.destination_info) != id(initial_destination_city), (
        f"Destination info (id={id(ship.destination_info)}) should be a copy of destination city (id={id(initial_destination_city)})"
    )
    assert ship.destination_info.name == initial_destination_city.name

    assert ship.ship_spec == expected_ship_spec

    assert isinstance(ship.cargo, dict)
    for resource in ResourceName:
        assert resource in ship.cargo, f"Cargo for {resource} was not initialized"

    assert ship.location == pytest.approx(ship.start.location), (
        f"Ship should depart {ship.location} from owner location {ship.start.location} on initialization"
    )


def test_clear_cargo(ship: Ship) -> None:
    ship.cargo[ResourceName.FOOD] = 10
    ship.gold = 50
    ship.clear_cargo()

    for resource in ResourceName:
        assert ship.cargo[resource] == 0, f"Cargo for {resource} should be cleared to 0"
    assert ship.gold == 0


def test_depart_sets_destination_location_and_iteration(ship: Ship) -> None:
    new_destination_city = City("NewDestinationCity", np.array([200, 70]), 500)
    ship.depart(new_destination_city)

    assert ship.destination == new_destination_city

    assert ship.destination == new_destination_city
    assert id(ship.destination_info) != id(new_destination_city), (
        f"Destination info (id={id(ship.destination_info)}) should be a copy of destination city (id={id(new_destination_city)})"
    )
    assert ship.destination_info.name == new_destination_city.name

    assert np.allclose(ship.location, ship.start.location)

    assert ship._iterations_en_route == 0, "Iterations en route should be reset to 0 on depart"


def test_has_arrived_property_returns_status_of_ship_correctly(ship: Ship) -> None:
    ship.location = (0.0, 0.0)
    ship._destination.location = (1.5 * ship.ship_spec.speed, 0.0)  # Reachable in 2 iterations
    ship.travel()
    assert not ship.has_arrived
    ship.travel()
    assert ship.has_arrived


def test_travel_moves_ship(ship: Ship) -> None:
    prev_location = ship.location
    ship.travel()
    assert ship.location != pytest.approx(prev_location)


def test_travel_calls_arrive_at_destination_when_close(ship: Ship) -> None:
    ship.location = (99.0, 0.0)
    ship._destination.location = (100.0, 0.0)
    with patch.object(ship, "arrive_at_destination") as mock_arrival:
        ship.travel()
        mock_arrival.assert_called_once()


def test_arrive_home_transfers_cargo_gold_and_information(ship: Ship) -> None:
    expected_resource_amount = 5
    expected_gold = 100
    ship.cargo = dict.fromkeys(ResourceName, expected_resource_amount)
    ship.gold = expected_gold

    for r in ResourceName:
        ship.start[r] = 0
    ship.start.gold = 0
    ship.start.information = {}

    ship.arrive_home()

    assert all(ship.start[r] == expected_resource_amount for r in ResourceName), (
        f"Owner should have received {expected_resource_amount} tons of each resource"
    )
    assert ship.start.gold == expected_gold, "Owner should have received all gold from the ship"
    assert ship.start.information.get(ship.destination.name) == ship.destination_info

    assert all(resource_amount == 0 for resource_amount in ship.cargo.values()), (
        "All cargo should be transferred to the owner"
    )
    assert ship.gold == 0, "All gold should be transferred to the owner"


def test_arrive_at_destination_sells_of_cargo_receives_information_and_gold(ship: Ship) -> None:
    expected_resource_amount = 5
    # expected_resource_price = 10
    expected_resources = dict.fromkeys(ResourceName, expected_resource_amount)
    initial_gold = 10_000

    destination_city = City("DestinationCity", gold=initial_gold, **dict.fromkeys(ResourceName, 0))
    destination_city.excess_supply = MagicMock(
        return_value=0,
    )  # Mocking excess supply to ensure no cargo will be bought
    expected_cargo_worth_in_gold = sum(
        amount * destination_city.price(resource) for resource, amount in expected_resources.items()
    )

    # destination_city.price = MagicMock(return_value=expected_resource_price)
    # destination_city.excess_supply = MagicMock(return_value=10000)

    ship.gold = 0
    ship.cargo = copy.copy(expected_resources)
    ship.set_new_destination(destination_city)
    ship.arrive_at_destination()

    assert ship.destination == ship.start, "Ship should return to owner after arriving at destination"

    assert ship.cargo == dict.fromkeys(ResourceName, 0), "All cargo should be sold off"
    for resource in ResourceName:
        assert destination_city[resource] == expected_resources[resource], (
            f"Destination should have received {expected_resources[resource]} tons of {resource}, but got {destination_city[resource]}"
        )
    assert ship.gold == pytest.approx(expected_cargo_worth_in_gold + CITY_INFORMATION_PRICE_IN_GOLD), (
        f"Ship should have received gold worth of its cargo ({expected_cargo_worth_in_gold}) and information ({CITY_INFORMATION_PRICE_IN_GOLD}), but got {ship.gold}"
    )
    assert destination_city.gold == pytest.approx(initial_gold - ship.gold), (
        f"Destination should have reduced its initial amount of gold ({initial_gold}) by the amount paid for the cargo ({expected_cargo_worth_in_gold}) and information ({CITY_INFORMATION_PRICE_IN_GOLD}), but got {destination_city.gold}"
    )
    assert destination_city.information[ship.start.name] == ship.owner_info, (
        "Destination should have received the owner's information"
    )


def test_get_resource_names_ordered_by_margin(ship: Ship) -> None:
    ship.destination.price = MagicMock(return_value=20)
    ship.owner_info.price = MagicMock(return_value=10)
    result = list(ship.get_resource_names_ordered_by_margin())
    assert set(result) == set(ResourceName)


def test_cargo_to_buy(ship: Ship) -> None:
    ship.owner_info.demand = MagicMock(return_value=10)
    result = list(ship.cargo_to_buy)
    assert all(isinstance(r, tuple) for r in result)

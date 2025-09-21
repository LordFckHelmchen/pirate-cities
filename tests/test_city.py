import copy

from pirate_cities.city import CITY_INFORMATION_PRICE_IN_GOLD
from pirate_cities.city import City
from pirate_cities.resource import ResourceName


def test_init_assigns_name_resources_and_gold() -> None:
    expected_city_name = "Shity"
    expected_gold = 100
    expected_resources = {resource: i * 10 for i, resource in enumerate(ResourceName)}
    city = City(expected_city_name, gold=expected_gold, **expected_resources)

    assert city.name == expected_city_name
    assert city.gold == expected_gold

    for resource in ResourceName:
        assert city[resource] == expected_resources[resource], (
            f"{resource} should be initialized to {expected_resources[resource]}"
        )


def test_update_market_info_adds_city_itself_and_returns_price() -> None:
    some_city = City("Some City")
    other_city_info = City("Other City")

    # city_a receives info about city_b (should add it)
    price = some_city.buy_city_info(other_city_info)

    assert "Other City" in some_city.information
    assert some_city.information["Other City"] == other_city_info
    assert price == CITY_INFORMATION_PRICE_IN_GOLD, "Price should be equal to the cost of 1 new information"


def test_update_market_info_updates_only_newer_info() -> None:
    initial_recency = 0
    updated_recency = 5
    other_city_info = City("Old City Info", recency_in_iterations=initial_recency)
    destination_city_info = City(
        "New City Info",
        recency_in_iterations=initial_recency,
        information={"Old City Info": copy.deepcopy(other_city_info)},
    )

    some_city = City(
        "Some City",
        information={
            "Old City Info": copy.deepcopy(other_city_info),
            "New City Info": copy.deepcopy(destination_city_info),
        },
    )
    destination_city_info.recency_in_iterations = updated_recency  # Newer than the existing info

    price = some_city.buy_city_info(destination_city_info)

    assert some_city.information["Old City Info"].recency_in_iterations == initial_recency
    assert some_city.information["New City Info"].recency_in_iterations == updated_recency
    assert price == CITY_INFORMATION_PRICE_IN_GOLD, "Price should be equal to the cost of 1 new information"

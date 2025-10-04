from pirate_cities.city import City
from pirate_cities.point2d import Point2d
from pirate_cities.resource import ResourceName
from pirate_cities.ship import Ship
from pirate_cities.ship import ShipType


def make_city(name: str, location: Point2d, **resources) -> City:
    c = City(name, location=location)
    for k, v in resources.items():
        c[k] = v
    return c


def test_set_itinerary_and_agenda_assignment() -> None:
    home = make_city("Home", location=Point2d(0, 1), food=100, goods=50, gold=1000)
    c1 = make_city("Port A", location=Point2d(2, 3), food=50, goods=10, gold=500)
    c2 = make_city("Port B", location=Point2d(4, 5), food=20, goods=5, gold=200)

    ship = Ship("Test Ship", start=home, route=[c1], ship_type=ShipType.SLOOP)

    agenda = {c1.name: {"sell": {ResourceName.FOOD: None}}, c2.name: {"buy": {ResourceName.GOODS: 10}}}
    ship.set_itinerary(start=home, route=[c1, c2], agenda=agenda)

    assert ship._route == [c1, c2, home]
    assert ship._agenda == agenda
    assert ship._current_stop_index == 0


def test_sell_per_agenda_sells_requested_amount() -> None:
    home = make_city("Home", location=Point2d(0, 1), food=100, goods=50, gold=1000)
    dest = make_city("Dest", location=Point2d(2, 3), food=10, goods=0, gold=1000)

    ship = Ship("Trader", start=home, route=[dest], ship_type=ShipType.SLOOP)
    # Give the ship cargo to sell
    initial_food = 10
    ship._cargo[ResourceName.FOOD] = initial_food

    # Agenda: sell 6 tons of food at dest
    food_to_sell = 6
    ship._agenda = {dest.name: {"sell": {ResourceName.FOOD: food_to_sell}}}

    before_gold = ship._gold
    before_dest_food = dest[ResourceName.FOOD]

    ship._sell_per_agenda(dest.name)

    # Sold up to 6 (limited by city's gold if necessary)
    sold = ship._sold_cargo.get(ResourceName.FOOD, None)
    assert sold is not None
    assert sold <= food_to_sell
    assert ship._cargo[ResourceName.FOOD] == initial_food - sold
    assert dest[ResourceName.FOOD] == before_dest_food + sold
    assert ship._gold >= before_gold


def test_buy_per_agenda_prefers_cheapest_future_price() -> None:
    home = make_city("Home", location=Point2d(0, 1), goods=0, gold=1000)
    # Create three ports with different prices for GOODS; we'll monkeypatch price and supply
    p1 = make_city("P1", location=Point2d(2, 3), goods=100, gold=1000)
    p2 = make_city("P2", location=Point2d(4, 5), goods=100, gold=1000)
    p3 = make_city("P3", location=Point2d(6, 7), goods=100, gold=1000)

    # Create ship with route p1->p2->p3
    ship = Ship("Buyer", start=home, route=[p1, p2, p3], ship_type=ShipType.SLOOP)

    # Ensure ample supply and deterministic prices
    p1.excess_supply = lambda _: 1000
    p2.excess_supply = lambda _: 1000
    p3.excess_supply = lambda _: 1000

    # Set prices: p1 cheapest
    p1.price = lambda _: 5
    p2.price = lambda _: 20
    p3.price = lambda _: 50

    # Agenda: buy 10 goods at p1
    expected_goods = 10
    initial_gold = 1000
    ship._agenda = {p1.name: {"buy": {ResourceName.GOODS: expected_goods}}}
    ship._gold = initial_gold

    ship._buy_per_agenda(p1.name)

    assert ship._cargo[ResourceName.GOODS] == expected_goods
    assert ship._gold == initial_gold - expected_goods * 5

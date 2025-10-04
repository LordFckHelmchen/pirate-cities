import random

import arcade

from pirate_cities.config import KM_TO_PX
from pirate_cities.config import SCREEN_SIZE_IN_PX
from pirate_cities.config import SCREEN_TITLE
from pirate_cities.config import UPDATE_RATE_IN_FPS
from pirate_cities.simulation import Simulation

# Visualization constants
SHIP_RADIUS = 5
CITY_RADIUS = 2 * SHIP_RADIUS
TEXT_COLOR = arcade.color.WHITE
BACKGROUND_COLOR = arcade.color.DARK_SLATE_GRAY


class PirateCitiesWindow(arcade.Window):
    def __init__(self, width: int, height: int, title: str, simulation: Simulation) -> None:
        super().__init__(width, height, title, resizable=True)
        self.simulation = simulation

        # Build a list of named colors from arcade.color and pick randomly from it
        colors = {v for k, v in vars(arcade.color).items() if isinstance(v, arcade.color.Color)}

        n_cities = len(self.simulation.cities)
        n_ships = len(self.simulation.ships)
        if n_cities + n_ships > len(colors):
            msg = "Not enough distinct colors to assign to cities and ships"
            raise ValueError(msg)

        self.city_colors: dict[str, arcade.color.Color] = dict(
            zip(
                (city.name for city in self.simulation.cities),
                random.sample(list(colors), n_cities),
                strict=False,
            ),
        )
        colors -= set(self.city_colors.values())  # Remove city colors from available colors
        self.ship_colors: dict[str, arcade.color.Color] = dict(
            zip(
                (ship.name for ship in self.simulation.ships),
                random.sample(list(colors), n_ships),
                strict=False,
            ),
        )

        self.set_update_rate(1 / UPDATE_RATE_IN_FPS)

    def on_draw(self) -> None:
        self.clear()
        # Draw cities
        for city in self.simulation.cities:
            x, y = (city.location * KM_TO_PX).as_int()
            arcade.draw_circle_filled(x, y, CITY_RADIUS, self.city_colors[city.name])
            arcade.draw_text(
                f"{city.name}\nPop: {city.population:.0f}\nFood: {city.food:.0f}\nGoods: {city.goods:.0f}\nLux: {city.luxuries:.0f}\nCannons: {city.cannons:.0f}\nGold: {city.gold:.0f}",
                x - CITY_RADIUS,
                y + CITY_RADIUS + 5,
                TEXT_COLOR,
                12,
                width=2 * CITY_RADIUS,
                align="center",
            )
        # Draw ships
        for ship in self.simulation.ships:
            # Interpolate position between start and destination
            x, y = (ship.current_location * KM_TO_PX).as_int()
            # Prefer ship-specific color, otherwise fall back to start city's color
            arcade.draw_circle_filled(x, y, SHIP_RADIUS, self.ship_colors[ship.name])
            arcade.draw_text(
                ship.name,
                x - SHIP_RADIUS,
                y + SHIP_RADIUS + 2,
                TEXT_COLOR,
                10,
                width=2 * SHIP_RADIUS,
                align="center",
            )

    def on_update(self, delta_time: float) -> None:  # noqa: ARG002
        # Advance simulation by one iteration
        self.simulation.step()


# Screen title and size
def main() -> None:
    n_cities = 4
    simulation = Simulation(n_cities)
    _ = PirateCitiesWindow(*SCREEN_SIZE_IN_PX.as_int(), title=SCREEN_TITLE, simulation=simulation)
    arcade.run()


if __name__ == "__main__":
    main()

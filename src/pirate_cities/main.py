import random

import numpy as np
import pandas as pd

from pirate_cities.city import CITY_NAMES
from pirate_cities.city import City
from pirate_cities.config import DEPARTURE_PROBABILITY_PER_ITERATION
from pirate_cities.config import INITIAL_SHIP_COUNT_RANGE
from pirate_cities.resource import ResourceName
from pirate_cities.ship import SHIP_NAMES
from pirate_cities.ship import Ship
from pirate_cities.ship import ShipType

pd.options.plotting.backend = "plotly"
pd.options.display.max_rows = None


def initialize(n_cities: int) -> tuple[list[City], list[Ship]]:
    cities = [City(name) for name in random.sample(CITY_NAMES, n_cities)]

    ships = []
    for owner_city in cities:
        n_ships = random.randint(*INITIAL_SHIP_COUNT_RANGE)  # Randomly decide the number of ships for this city
        destination_cities = random.sample(
            [dc for dc in cities if dc != owner_city],
            k=n_ships,
        )  # Choose different random destination cities that are not the owner city
        ship_names = random.sample(SHIP_NAMES, n_ships)  # Randomly select ship names for the ships of this city
        for ship_name, destination_city in zip(ship_names, destination_cities, strict=False):
            ship = Ship(
                name=ship_name,
                start=owner_city,
                destination=destination_city,
                ship_type=random.choice(list(ShipType)),
            )
            ships.append(ship)
    return cities, ships


def main(n_cities: int, n_iterations: int, log_data: bool = False) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:  # noqa: C901, FBT001, FBT002
    cities, ships = initialize(n_cities)

    if log_data:
        cities_data = []
        ships_data = []

    for i in range(n_iterations):
        for ship in ships:
            if not ship.has_arrived:
                if log_data:
                    ship_data = {
                        "iteration": i,
                        "name": ship.name,
                        "destination": ship.destination.name,
                        "description": ship.as_string(),
                        "iteration_en_route": ship.iterations_en_route,
                    }
                ship.travel()
                if log_data and ship.has_arrived:
                    print(
                        f"  ARRIVAL OF SHIP {ship_data['description']} after {ship_data['iteration_en_route']} iterations.",
                    )
                    ships_data.append(ship_data)

            elif random.random() < DEPARTURE_PROBABILITY_PER_ITERATION:  # Randomly decide to depart
                ship.depart(
                    random.choice(
                        [city for city in cities if city.name != ship.start.name],
                    ),
                )
                if log_data:
                    print(f"DEPARTURE OF SHIP {ship.as_string()}")

        for city in cities:
            if log_data:
                # Collect city data for each iteration
                cities_data.append(
                    {
                        "iteration": i,
                        "name": city.name,
                        "food": city.food,
                        # "food_demand": city.demand(ResourceName.FOOD),
                        "food_price": city.price(ResourceName.FOOD),
                        "goods": city.goods,
                        # "goods_demand": city.demand(ResourceName.GOODS),
                        "goods_price": city.price(ResourceName.GOODS),
                        "luxuries": city.luxuries,
                        # "luxuries_demand": city.demand(ResourceName.LUXURIES),
                        "luxuries_price": city.price(ResourceName.LUXURIES),
                        "cannons": city.cannons,
                        # "cannons_demand": city.demand(ResourceName.CANNONS),
                        "cannons_price": city.price(ResourceName.CANNONS),
                        "population": city.population,
                        # "capacity": city.capacity,
                        "gold": city.gold,
                    },
                )
            city.step()

    if log_data:
        cities_data = pd.DataFrame(cities_data).sort_values(by=["name", "iteration"])
        ships_data = pd.DataFrame(ships_data).sort_values(by=["name", "iteration"])
        return cities_data, ships_data
    return None, None


def plot_cities(cities: pd.DataFrame, ships: pd.DataFrame) -> None:
    """Plot each column over iterations for each city."""

    city_names = sorted(cities["name"].unique())
    city_columns_to_plot = [col for col in cities if col not in ["iteration", "name", "capacity"]]

    ship_names = sorted(ships["name"].unique())

    # Make sure the colors are consistent across subplots
    color_palette = px.colors.qualitative.Plotly
    city_colors = {city: color_palette[i % len(color_palette)] for i, city in enumerate(city_names)}
    ship_colors = {
        ship: color_palette[i % len(color_palette)] for i, ship in enumerate(ship_names, start=len(city_names))
    }

    plot_rows = 2
    plot_cols = int(np.ceil((len(city_columns_to_plot) + 1) / plot_rows))
    fig = make_subplots(
        rows=plot_rows,
        cols=plot_cols,
        shared_xaxes=True,
        horizontal_spacing=0.03,
        vertical_spacing=0.02,
    )

    # Resource plots
    for i, col in enumerate(city_columns_to_plot):
        row_id = int(i / plot_cols) + 1
        col_id = (i % plot_cols) + 1
        for city_name in city_names:
            city_mask = cities["name"] == city_name
            fig.add_trace(
                go.Scatter(
                    x=cities.loc[city_mask, "iteration"],
                    y=cities.loc[city_mask, col],
                    mode="lines",
                    name=city_name,
                    legendgroup=city_name,
                    showlegend=(i == 0),  # Show legend only in first subplot
                    line={"color": city_colors[city_name]},
                ),
                row=row_id,
                col=col_id,
            )
        # Use log-scale for prices
        axis_props = {"title_text": col.capitalize()}
        if col.endswith("price"):
            axis_props["type"] = "log"
            axis_props["title_text"] += f" ({axis_props['type']})"
        fig.update_yaxes(**axis_props, row=row_id, col=col_id)
    for ship_name in ship_names:
        ship_mask = ships["name"] == ship_name
        fig.add_trace(
            go.Scatter(
                x=ships.loc[ship_mask, "iteration"],
                y=ships.loc[ship_mask, "destination"],
                hovertext=ships.loc[ship_mask, "description"],
                mode="lines+markers",
                name=ship_name,
                legendgroup=ship_name,
                showlegend=True,
                marker={"color": ship_colors[ship_name]},
            ),
            row=row_id,
            col=col_id + 1,
        )
    fig.update_layout(
        title="City Resources Over Time",
        showlegend=True,
    )
    fig.update_xaxes(title_text="Iteration", row=plot_rows)
    fig.update_yaxes(minallowed=0)
    fig.show()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Pirate Cities simulation.")
    parser.add_argument(
        "-n",
        "--n_cities",
        type=int,
        default=4,
        help="Number of cities in the simulation.",
    )
    parser.add_argument(
        "-i",
        "--n_iterations",
        type=int,
        default=30,
        help="Number of iterations to run the simulation.",
    )
    args = parser.parse_args()

    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        log_data = True
    except ImportError:
        print("Plotly is not installed. Can't plot anything.")
        log_data = False

    print("Hello from pirate-cities!")
    cities_data, ships_data = main(
        n_cities=args.n_cities,
        n_iterations=args.n_iterations,
        log_data=log_data,
    )
    plot_cities(cities_data, ships_data)

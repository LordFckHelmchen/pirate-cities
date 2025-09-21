from enum import StrEnum

import pandas as pd


class ResourceName(StrEnum):
    FOOD = "food"
    GOODS = "goods"
    LUXURIES = "luxuries"
    CANNONS = "cannons"


BASE_RESOURCE_PRICE_IN_GOLD = pd.Series(
    {
        "food": 3,
        "goods": 5,
        "luxuries": 10,
        "cannons": 1,
    },
    name="base_price_in_gold",
)
RESOURCE_PRICE_LIMITS = (1 / 1_000_000, 200)  # To avoid zero/inf with no demand/supply
RESOURCE_PRICE_RANGE = RESOURCE_PRICE_LIMITS[1] - RESOURCE_PRICE_LIMITS[0]
RESOURCE_PRICE_ELASTICITY = 0.5

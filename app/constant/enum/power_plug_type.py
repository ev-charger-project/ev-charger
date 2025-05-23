from enum import Enum


class PlugRegion(str, Enum):
    NORTH_AMERICA = "North America"
    EUROPE = "Europe"
    TESLA_VEHICLES = "Tesla vehicles"
    NISSAN_LEAF = "Nissan Leaf"


class PowerModel(str, Enum):
    AC = "AC"
    DC = "DC"

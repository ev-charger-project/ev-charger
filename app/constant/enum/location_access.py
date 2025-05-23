from enum import Enum


class LocationAccess(str, Enum):
    public = "public"
    restricted = "restricted"

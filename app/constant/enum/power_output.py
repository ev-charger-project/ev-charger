from enum import Enum


class ChargingSpeed(str, Enum):
    SLOW = "Slow"
    FAST = "Fast"
    ULTRA_FAST = "Ultra-Fast"

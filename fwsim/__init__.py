"""Local firmware-update simulator for pytest. No hardware or downloads needed."""
from .faults import (
    BootFailure,
    CorruptImage,
    PowerLoss,
    ResumeNotPossible,
    SettingsLost,
    WifiDrop,
)
from .firmware import FirmwareImage
from .simulator import (
    DOWNLOAD_FAILED_MESSAGE,
    MAX_FAILED_BOOTS,
    RETRY_CUTOFF_S,
    RETRY_INTERVAL_S,
    Event,
    Simulator,
    State,
)

__all__ = [
    "BootFailure",
    "CorruptImage",
    "DOWNLOAD_FAILED_MESSAGE",
    "Event",
    "FirmwareImage",
    "MAX_FAILED_BOOTS",
    "PowerLoss",
    "RETRY_CUTOFF_S",
    "RETRY_INTERVAL_S",
    "ResumeNotPossible",
    "SettingsLost",
    "Simulator",
    "State",
    "WifiDrop",
]

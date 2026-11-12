"""Configurable failures to inject into a simulation.

Pass a list of these to ``Simulator(faults=[...])``. Each fault fires at most
as often as configured. For one-off control during a test you can also call
``sim.wifi_down()``, ``sim.wifi_up()`` and ``sim.power_cycle()`` directly.
"""
from __future__ import annotations

from dataclasses import dataclass

STAGES = ("download", "install", "boot")


@dataclass(frozen=True)
class WifiDrop:
    """Wi-Fi goes down when the download reaches ``at_percent``.

    It stays down for ``duration_s``. With ``repeat`` > 1 it drops again
    ``interval_s`` seconds after each restore (e.g. TC-05: 5 drops, ~20 s apart).
    """
    at_percent: float
    duration_s: int
    repeat: int = 1
    interval_s: int = 0


@dataclass(frozen=True)
class PowerLoss:
    """Power is cut (e.g. TV turned off) at a given stage.

    - ``download`` / ``install``: fires when that stage reaches ``at_percent``.
    - ``boot``: interrupts one boot attempt of the new firmware, which counts
      as a failed boot (REQ-40).
    Power returns after ``off_s`` seconds.
    """
    stage: str
    at_percent: float = 50
    off_s: int = 5

    def __post_init__(self) -> None:
        if self.stage not in STAGES:
            raise ValueError(f"stage must be one of {STAGES}, got {self.stage!r}")


@dataclass(frozen=True)
class CorruptImage:
    """The completed download fails the integrity check (REQ-11)."""


@dataclass(frozen=True)
class ResumeNotPossible:
    """The next ``times`` resumes must restart from 0% (REQ-25).

    Models a damaged partial file or a changed image on the server.
    """
    times: int = 1


@dataclass(frozen=True)
class BootFailure:
    """The new firmware fails to reach the home screen ``times`` boots in a row."""
    times: int = 1


@dataclass(frozen=True)
class SettingsLost:
    """Injected bug: user settings are wiped on ``update`` or ``rollback``.

    Use it to check that a settings-preservation test really catches a
    failure (REQ-50, REQ-51).
    """
    on: str = "update"

    def __post_init__(self) -> None:
        if self.on not in ("update", "rollback"):
            raise ValueError(f"on must be 'update' or 'rollback', got {self.on!r}")

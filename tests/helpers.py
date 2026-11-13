"""Shared setup for the simulator tests."""
from __future__ import annotations

from fwsim import FirmwareImage, Simulator

SETTINGS = {
    "language": "en",
    "wifi_network": "home",
    "display": "4K",
    "account": "test-user",
}


def make(*faults: object, mandatory: bool = False, settings: dict | None = None) -> Simulator:
    """Device on 1.0 (slot A) with 2.0 offered and the given faults."""
    return Simulator(
        installed="1.0",
        offered=FirmwareImage("2.0", mandatory=mandatory),
        settings=SETTINGS if settings is None else settings,
        faults=list(faults),
    )


def download(sim: Simulator) -> Simulator:
    sim.start_download()
    sim.run()
    return sim


def download_and_install(sim: Simulator) -> Simulator:
    download(sim)
    assert sim.state == "DOWNLOADED"
    sim.install()
    sim.run()
    return sim


def events(sim: Simulator, name: str) -> list:
    return [e for e in sim.events if e.name == name]

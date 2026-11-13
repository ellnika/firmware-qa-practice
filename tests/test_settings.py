"""User settings survive update and rollback (requirements.md §6)."""
import pytest

from fwsim import BootFailure, PowerLoss, SettingsLost
from helpers import SETTINGS, download_and_install, make


def test_settings_kept_after_update():
    """TC-21 | REQ-50"""
    sim = download_and_install(make())
    sim.reboot()

    assert sim.active_version == "2.0"
    assert sim.settings == SETTINGS


def test_settings_kept_after_rollback():
    """TC-22 | REQ-51"""
    sim = download_and_install(make(BootFailure(times=3)))
    sim.reboot()

    assert sim.state == "ROLLED_BACK"
    assert sim.settings == SETTINGS


@pytest.mark.parametrize("on, boot_failures", [("update", 0), ("rollback", 3)])
def test_settings_loss_is_detected(on, boot_failures):
    """REQ-50, REQ-51: with a settings bug injected, the check above must fail.
    This proves the settings tests can actually catch a lost setting."""
    faults = [SettingsLost(on=on)] + ([BootFailure(times=boot_failures)] if boot_failures else [])
    sim = download_and_install(make(*faults))
    sim.reboot()

    assert sim.settings != SETTINGS


def test_settings_kept_after_power_loss_during_install():
    """TC-12 | REQ-13, REQ-50"""
    sim = download_and_install(make(PowerLoss(stage="install", at_percent=50)))
    assert sim.settings == SETTINGS

    sim.install()
    sim.run()
    sim.reboot()
    assert sim.active_version == "2.0"
    assert sim.settings == SETTINGS

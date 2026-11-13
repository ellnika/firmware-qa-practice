"""Reboot into the new firmware and rollback (requirements.md §2, §5)."""
from fwsim import BootFailure, PowerLoss
from helpers import download_and_install, events, make


def test_reboot_applies_update():
    """TC-08 | REQ-12"""
    sim = download_and_install(make())
    assert sim.state == "REBOOT_PENDING"
    assert sim.active_version == "1.0"  # not applied before reboot

    sim.reboot()

    assert sim.state == "UPDATED"
    assert sim.active_slot == "B"
    assert sim.active_version == "2.0"
    assert sim.is_working


def test_wifi_drop_during_reboot():
    """TC-08 | REQ-13"""
    sim = download_and_install(make())
    sim.wifi_down()

    sim.reboot()

    assert sim.state == "UPDATED"
    assert sim.active_version == "2.0"
    sim.wifi_restore()
    assert sim.is_working


def test_power_loss_during_boot_counts_as_failed_boot():
    """TC-13 | REQ-13, REQ-40"""
    sim = download_and_install(make(PowerLoss(stage="boot")))

    sim.reboot()

    assert events(sim, "boot_failed")[0].data["reason"] == "power_loss"
    assert sim.failed_boots == 1
    assert sim.state == "UPDATED"
    assert sim.active_version == "2.0"


def test_two_failed_boots_still_updates():
    """REQ-41 (boundary: fewer than 3 failures)"""
    sim = download_and_install(make(BootFailure(times=2)))

    sim.reboot()

    assert sim.failed_boots == 2
    assert sim.state == "UPDATED"
    assert sim.active_version == "2.0"


def test_three_failed_boots_roll_back():
    """TC-20 | REQ-41, REQ-42"""
    sim = download_and_install(make(BootFailure(times=3)))

    sim.reboot()

    assert sim.failed_boots == 3
    assert events(sim, "rollback")
    assert sim.state == "ROLLED_BACK"
    assert sim.active_slot == "A"
    assert sim.active_version == "1.0"
    assert sim.is_working

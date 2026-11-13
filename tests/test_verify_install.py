"""Integrity check and install to the inactive slot (requirements.md §2, §7)."""
import pytest

from fwsim import CorruptImage, PowerLoss, WifiDrop
from helpers import download, download_and_install, events, make


def test_incomplete_image_rejected():
    """TC-06 | REQ-11, REQ-64"""
    sim = make(WifiDrop(at_percent=40, duration_s=30))
    sim.start_download()
    sim.advance(45)

    sim.force_verify()

    assert sim.state == "VERIFY_FAILED"
    assert events(sim, "verify_rejected")[0].data["reason"] == "incomplete"
    assert sim.downloaded_mb == 0  # rejected image deleted
    assert sim.slots["B"] is None
    assert sim.active_version == "1.0"

    sim.advance(120)  # Wi-Fi is back; nothing is downloaded again by itself
    assert sim.state == "VERIFY_FAILED"


def test_corrupt_image_rejected():
    """TC-06 | REQ-11"""
    sim = download(make(CorruptImage()))

    assert sim.state == "VERIFY_FAILED"
    assert events(sim, "verify_rejected")[0].data["reason"] == "checksum_mismatch"
    with pytest.raises(RuntimeError):
        sim.install()  # never installed
    assert sim.slots["B"] is None
    assert sim.active_version == "1.0"


def test_wifi_drop_during_install_no_effect():
    """TC-07 | REQ-14"""
    sim = download(make())
    sim.install()
    sim.advance(10)
    sim.wifi_down()
    sim.run()

    assert sim.state == "REBOOT_PENDING"
    assert sim.slots["B"] == "2.0"
    assert sim.active_version == "1.0"


def test_power_loss_during_install_keeps_old_slot():
    """TC-12 | REQ-12, REQ-13"""
    sim = download_and_install(make(PowerLoss(stage="install", at_percent=50)))

    assert sim.state == "DOWNLOADED"  # verified image kept for another try
    assert sim.active_slot == "A"
    assert sim.active_version == "1.0"
    assert sim.slots["B"] is None  # half-written slot not used
    assert sim.is_working

    sim.install()
    sim.run()
    sim.reboot()
    assert sim.active_version == "2.0"


def test_install_not_automatic():
    """REQ-65"""
    sim = download(make())
    sim.advance(600)

    assert sim.state == "DOWNLOADED"
    assert sim.slots["B"] is None

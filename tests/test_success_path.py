"""Success path: a clean update from 1.0 to 2.0 with no faults.

Checks every stage, not only the end result, so a defect in any step shows up
here first. Requirements: REQ-10, REQ-11, REQ-12, REQ-50, REQ-65.
Related manual test cases: TC-08, TC-21.
"""
from helpers import events

EXPECTED_EVENTS = [
    "download_started",
    "download_complete",
    "verify_ok",
    "install_started",
    "install_complete",
    "reboot",
    "booted",
]


def test_success_path_end_to_end(any_update_device, user_settings):
    """REQ-10, REQ-11, REQ-12, REQ-50, REQ-65"""
    sim = any_update_device

    # Download: complete and verified, current firmware still active (REQ-10, REQ-11).
    sim.start_download()
    sim.run()
    assert sim.state == "DOWNLOADED"
    assert sim.progress_percent == 100
    assert events(sim, "verify_ok")[0].data["checksum"] == sim.offered.checksum
    assert sim.retry_count == 0
    assert sim.message is None
    assert sim.active_version == "1.0"
    assert sim.slots["B"] is None  # REQ-65: nothing installed without the user

    # Install to the inactive slot; not applied until reboot (REQ-12).
    sim.install()
    sim.run()
    assert sim.state == "REBOOT_PENDING"
    assert sim.slots["B"] == "2.0"
    assert sim.active_slot == "A"
    assert sim.active_version == "1.0"

    # Reboot into 2.0.
    sim.reboot()
    assert sim.state == "UPDATED"
    assert sim.active_slot == "B"
    assert sim.active_version == "2.0"
    assert sim.slots["A"] == "1.0"  # previous firmware kept for rollback
    assert sim.failed_boots == 0
    assert sim.is_working
    assert sim.message is None
    assert sim.settings == user_settings  # REQ-50

    # Nothing unexpected happened along the way.
    assert sim.event_names() == EXPECTED_EVENTS
    assert events(sim, "booted")[0].data == {"slot": "B", "version": "2.0"}


def test_success_path_timing(device):
    """Download and install take the expected simulated time, with no waits."""
    sim = device
    sim.start_download()
    sim.run()
    expected_download_s = sim.offered.size_mb / sim.download_rate_mb_s
    assert events(sim, "download_complete")[0].t == expected_download_s

    sim.install()
    sim.run()
    started = events(sim, "install_started")[0].t
    completed = events(sim, "install_complete")[0].t
    assert completed - started == sim.install_s


def test_download_started_reports_update_type(any_update_device):
    """The download records which version is offered and whether it is mandatory."""
    sim = any_update_device
    sim.start_download()
    data = events(sim, "download_started")[0].data
    assert data == {"version": "2.0", "mandatory": sim.offered.mandatory}

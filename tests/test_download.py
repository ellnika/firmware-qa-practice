"""Wi-Fi and power interruptions during download (requirements.md §3, §4, §7)."""
import pytest

from fwsim import DOWNLOAD_FAILED_MESSAGE, PowerLoss, ResumeNotPossible, WifiDrop
from helpers import download, events, make


def test_wifi_drop_keeps_current_firmware():
    """TC-01 | REQ-10"""
    sim = make(WifiDrop(at_percent=40, duration_s=30))
    sim.start_download()
    sim.advance(45)

    assert sim.state == "RETRY_WAIT"
    assert sim.active_version == "1.0"
    assert sim.slots["B"] is None


def test_brief_drop_resumes_on_reconnect():
    """TC-02 | REQ-22, REQ-25, REQ-60"""
    sim = make(WifiDrop(at_percent=40, duration_s=30))
    sim.start_download()
    sim.advance(70)  # drop at t=40, Wi-Fi back at t=70

    assert sim.state == "DOWNLOADING"
    assert sim.progress_percent == 40  # resumed, not restarted
    assert events(sim, "download_resumed")[0].t == 70  # immediately, no 60 s wait
    assert sim.retry_count == 0
    assert sim.message is None

    sim.run()
    assert sim.state == "DOWNLOADED"
    assert sim.active_version == "1.0"
    assert sim.is_working


def test_long_drop_optional_requires_manual_retry():
    """TC-03 | REQ-23, REQ-30, REQ-31, REQ-33"""
    sim = download(make(WifiDrop(at_percent=40, duration_s=360)))

    assert sim.state == "DOWNLOAD_FAILED"
    assert sim.message == DOWNLOAD_FAILED_MESSAGE
    assert sim.downloaded_mb == 40  # partial download kept
    assert sim.active_version == "1.0"

    sim.advance(100)  # Wi-Fi returns at t=400
    assert sim.wifi_up
    assert sim.state == "DOWNLOAD_FAILED"  # no automatic resume
    assert sim.is_working


def test_manual_retry_completes_download():
    """TC-03 | REQ-23, REQ-25"""
    sim = download(make(WifiDrop(at_percent=40, duration_s=360)))
    sim.advance(100)

    sim.retry()
    sim.run()

    assert sim.state == "DOWNLOADED"
    assert sim.message is None
    assert events(sim, "download_resumed")[-1].data["percent"] == 40


def test_manual_retry_offline_fails_once():
    """REQ-63"""
    sim = download(make(WifiDrop(at_percent=40, duration_s=360)))
    assert not sim.wifi_up

    sim.retry()

    assert sim.state == "DOWNLOAD_FAILED"
    assert sim.message == DOWNLOAD_FAILED_MESSAGE
    assert len(events(sim, "manual_retry_failed")) == 1


def test_retry_timing_five_retries_60s_apart():
    """TC-03, TC-04 | REQ-20, REQ-21"""
    sim = download(make(WifiDrop(at_percent=40, duration_s=360)))

    drop_t = events(sim, "download_interrupted")[0].t
    retry_offsets = [e.t - drop_t for e in events(sim, "auto_retry_failed")]
    assert retry_offsets == [60, 120, 180, 240, 300]
    assert events(sim, "retries_stopped_user_must_retry")[0].t - drop_t == 300


@pytest.mark.parametrize(
    "drop_s, expected",
    [(299, "DOWNLOADED"), (300, "DOWNLOADED"), (301, "DOWNLOAD_FAILED")],
)
def test_five_minute_cutoff_boundary(drop_s, expected):
    """TC-02, TC-03 | REQ-22, REQ-23 (boundary around 5 min)"""
    sim = download(make(WifiDrop(at_percent=40, duration_s=drop_s)))
    assert sim.state == expected


def test_long_drop_mandatory_restarts_on_reconnect():
    """TC-04 | REQ-24, REQ-30, REQ-32, REQ-33"""
    sim = make(WifiDrop(at_percent=40, duration_s=360), mandatory=True)
    sim.start_download()
    sim.advance(345)  # retries stopped at t=340, Wi-Fi still down

    assert sim.state == "WAITING_FOR_NETWORK"
    assert sim.message is None
    assert sim.active_version == "1.0"

    sim.run()
    assert events(sim, "auto_restart_on_reconnect")[0].t == 400
    assert len(events(sim, "auto_retry_failed")) == 5  # no endless retrying
    assert sim.state == "DOWNLOADED"


def test_repeated_drops_never_stuck():
    """TC-05 | REQ-30"""
    sim = download(make(WifiDrop(at_percent=20, duration_s=10, repeat=5, interval_s=20)))

    assert len(events(sim, "wifi_down")) == 5
    assert sim.state == "DOWNLOADED"
    assert sim.active_version == "1.0"


def test_each_drop_starts_new_retry_window():
    """TC-05 | REQ-62: four 4-min drops add up to more than 5 min offline,
    but each one is shorter than 5 min, so the download never gives up."""
    sim = download(make(WifiDrop(at_percent=20, duration_s=240, repeat=4, interval_s=10)))

    assert len(events(sim, "wifi_down")) == 4
    assert not events(sim, "retries_stopped_user_must_retry")
    assert sim.state == "DOWNLOADED"


def test_resume_not_possible_restarts_from_zero():
    """TC-23 | REQ-25"""
    sim = make(WifiDrop(at_percent=40, duration_s=30), ResumeNotPossible())
    sim.start_download()
    sim.advance(70)

    assert events(sim, "download_restarted_from_zero")
    assert sim.progress_percent == 0

    sim.run()
    assert sim.state == "DOWNLOADED"
    assert events(sim, "verify_ok")


def test_power_loss_during_download_resumes():
    """TC-11 | REQ-13, REQ-61"""
    sim = download(make(PowerLoss(stage="download", at_percent=50)))

    assert events(sim, "power_lost")
    assert events(sim, "booted")[0].data == {"slot": "A", "version": "1.0"}
    assert events(sim, "download_resumed")[0].data["percent"] == 50
    assert sim.state == "DOWNLOADED"
    assert sim.active_version == "1.0"


def test_reboot_while_waiting_for_network_keeps_waiting():
    """REQ-61 (second part)"""
    sim = make(WifiDrop(at_percent=40, duration_s=360), mandatory=True)
    sim.start_download()
    sim.advance(345)

    sim.power_cycle()

    assert sim.state == "WAITING_FOR_NETWORK"
    sim.run()
    assert sim.state == "DOWNLOADED"

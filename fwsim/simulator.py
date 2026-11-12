"""Firmware-update simulator implementing the rules in requirements.md.

Time is simulated in 1-second ticks, so a 6-minute Wi-Fi drop runs instantly.
Nothing touches real hardware or the network.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable

from .faults import (
    BootFailure,
    CorruptImage,
    PowerLoss,
    ResumeNotPossible,
    SettingsLost,
    WifiDrop,
)
from .firmware import FirmwareImage

RETRY_INTERVAL_S = 60  # REQ-21
RETRY_CUTOFF_S = 300  # REQ-20, REQ-23, REQ-24
MAX_FAILED_BOOTS = 3  # REQ-41
DOWNLOAD_FAILED_MESSAGE = (  # REQ-31
    "Update couldn't be downloaded. Check your connection and try again."
)


class State(str, Enum):
    IDLE = "IDLE"
    DOWNLOADING = "DOWNLOADING"
    RETRY_WAIT = "RETRY_WAIT"  # Wi-Fi lost, inside the 5-minute retry window
    DOWNLOAD_FAILED = "DOWNLOAD_FAILED"  # optional update, retries stopped (REQ-31)
    WAITING_FOR_NETWORK = "WAITING_FOR_NETWORK"  # mandatory update, retries stopped (REQ-32)
    DOWNLOADED = "DOWNLOADED"  # complete and verified
    VERIFY_FAILED = "VERIFY_FAILED"  # image rejected, not installed (REQ-11)
    INSTALLING = "INSTALLING"
    REBOOT_PENDING = "REBOOT_PENDING"  # installed to inactive slot (REQ-12)
    UPDATED = "UPDATED"  # booted into the new firmware
    ROLLED_BACK = "ROLLED_BACK"  # back on the previous firmware (REQ-41)

    def __str__(self) -> str:
        return self.value


# States in which nothing happens until the test acts.
_SETTLED = {
    State.IDLE,
    State.DOWNLOAD_FAILED,
    State.DOWNLOADED,
    State.VERIFY_FAILED,
    State.REBOOT_PENDING,
    State.UPDATED,
    State.ROLLED_BACK,
}
_DOWNLOAD_STATES = {State.DOWNLOADING, State.RETRY_WAIT, State.WAITING_FOR_NETWORK}


@dataclass(frozen=True)
class Event:
    t: int
    name: str
    data: dict[str, Any] = field(default_factory=dict)


class Simulator:
    """A device with A/B slots plus its update logic.

    Typical use::

        sim = Simulator(offered=FirmwareImage("2.0"), faults=[WifiDrop(40, 30)])
        sim.start_download()
        sim.run()
        assert sim.state == "DOWNLOADED"
    """

    def __init__(
        self,
        installed: str = "1.0",
        offered: FirmwareImage | None = None,
        settings: dict[str, Any] | None = None,
        faults: Iterable[object] = (),
        download_rate_mb_s: float = 1.0,
        install_s: int = 30,
    ) -> None:
        self.offered = offered or FirmwareImage("2.0")
        self.download_rate_mb_s = download_rate_mb_s
        self.install_s = install_s

        self.time = 0
        self.slots: dict[str, str | None] = {"A": installed, "B": None}
        self.active_slot = "A"
        self.settings: dict[str, Any] = dict(settings or {})
        self.wifi_up = True
        self.state = State.IDLE
        self.downloaded_mb = 0.0
        self.install_done_s = 0
        self.retry_count = 0  # automatic retries in the current 5-minute window
        self.failed_boots = 0
        self.message: str | None = None
        self.events: list[Event] = []

        self._failed_at: int | None = None
        self._wifi_schedule: list[tuple[int, bool]] = []
        self._fired: set[int] = set()  # ids of percent-triggered faults already used
        self._load_faults(list(faults))

    # ------------------------------------------------------------------ setup
    def _load_faults(self, faults: list[object]) -> None:
        known = (WifiDrop, PowerLoss, CorruptImage, ResumeNotPossible, BootFailure, SettingsLost)
        for f in faults:
            if not isinstance(f, known):
                raise TypeError(f"unknown fault: {f!r}")
        self._wifi_drops = [f for f in faults if isinstance(f, WifiDrop)]
        self._power_losses = [
            f for f in faults if isinstance(f, PowerLoss) and f.stage != "boot"
        ]
        self._boot_power_losses = [
            f for f in faults if isinstance(f, PowerLoss) and f.stage == "boot"
        ]
        self._corrupt = any(isinstance(f, CorruptImage) for f in faults)
        self._resume_failures = sum(f.times for f in faults if isinstance(f, ResumeNotPossible))
        self._boot_failures = sum(f.times for f in faults if isinstance(f, BootFailure))
        self._settings_lost = {f.on for f in faults if isinstance(f, SettingsLost)}

    # ------------------------------------------------------------- properties
    @property
    def active_version(self) -> str | None:
        return self.slots[self.active_slot]

    @property
    def inactive_slot(self) -> str:
        return "B" if self.active_slot == "A" else "A"

    @property
    def progress_percent(self) -> float:
        return 100.0 * self.downloaded_mb / self.offered.size_mb

    @property
    def is_working(self) -> bool:
        """Boots to home screen on a valid slot and is connected to Wi-Fi.

        Playback and remote input are not modelled; the simulated device
        handles them whenever it is booted.
        """
        return self.active_version is not None and self.wifi_up

    def event_names(self) -> list[str]:
        return [e.name for e in self.events]

    def __repr__(self) -> str:
        return (
            f"<Simulator t={self.time}s state={self.state} active={self.active_version} "
            f"progress={self.progress_percent:.0f}% wifi={'up' if self.wifi_up else 'down'}>"
        )

    # ---------------------------------------------------------- user actions
    def start_download(self) -> None:
        self._require(State.IDLE, State.VERIFY_FAILED)
        self.message = None
        self._log("download_started", version=self.offered.version,
                  mandatory=self.offered.mandatory)
        if self.downloaded_mb > 0:
            self._resume()
        else:
            self._set_state(State.DOWNLOADING)
        if not self.wifi_up:
            self._download_failed()

    def retry(self) -> None:
        """Manual retry by the user after an optional update failed (REQ-23)."""
        self._require(State.DOWNLOAD_FAILED)
        self._log("manual_retry")
        if self.wifi_up:
            self.message = None
            self._resume()
        else:
            self._log("manual_retry_failed")

    def force_verify(self) -> None:
        """Make the device verify what it has now, even if incomplete (TC-06)."""
        self._require(State.IDLE, *_DOWNLOAD_STATES, State.DOWNLOAD_FAILED)
        self._verify()

    def install(self) -> None:
        self._require(State.DOWNLOADED)
        self.slots[self.inactive_slot] = None  # slot is being overwritten
        self.install_done_s = 0
        self._log("install_started", slot=self.inactive_slot)
        self._set_state(State.INSTALLING)

    def reboot(self) -> None:
        self._log("reboot")
        self._restart()

    def power_cycle(self, off_s: int = 5) -> None:
        """Cut power now (e.g. TV off) and restore it after ``off_s`` seconds."""
        self._power_off(off_s)
        self._restart()

    def wifi_down(self) -> None:
        self._set_wifi(False)

    def wifi_restore(self) -> None:
        self._set_wifi(True)

    # ------------------------------------------------------------------- time
    def advance(self, seconds: int) -> None:
        for _ in range(seconds):
            self._tick()

    def run(self, max_s: int = 24 * 3600) -> None:
        """Advance time until nothing more happens without test input."""
        start = self.time
        while not self._settled():
            if self.time - start >= max_s:
                raise RuntimeError(f"simulation did not settle within {max_s}s: {self!r}")
            self._tick()

    def _settled(self) -> bool:
        if self.state in _SETTLED:
            return True
        if self.state is State.WAITING_FOR_NETWORK:
            return not self.wifi_up and not any(up for _, up in self._wifi_schedule)
        return False

    def _tick(self) -> None:
        self.time += 1
        self._apply_wifi_schedule()
        if self.state is State.DOWNLOADING:
            self._tick_download()
        elif self.state is State.RETRY_WAIT:
            self._tick_retry_wait()
        elif self.state is State.WAITING_FOR_NETWORK and self.wifi_up:
            self._log("auto_restart_on_reconnect")  # REQ-24
            self._resume()
        elif self.state is State.INSTALLING:
            self._tick_install()

    # --------------------------------------------------------------- download
    def _tick_download(self) -> None:
        size = self.offered.size_mb
        self.downloaded_mb = min(size, self.downloaded_mb + self.download_rate_mb_s)
        pct = self.progress_percent

        for f in self._wifi_drops:
            if id(f) not in self._fired and pct >= f.at_percent:
                self._fired.add(id(f))
                self._schedule_wifi_drops(f)
        if self.state is not State.DOWNLOADING:
            return
        if self._fire_power_loss("download", pct):
            return
        if self.downloaded_mb >= size:
            self._log("download_complete")
            self._verify()

    def _download_failed(self) -> None:
        self._failed_at = self.time  # REQ-20: timer starts at the failure
        self.retry_count = 0
        self._log("download_interrupted", percent=round(self.progress_percent, 1))
        self._set_state(State.RETRY_WAIT)

    def _tick_retry_wait(self) -> None:
        assert self._failed_at is not None
        if self.wifi_up:  # REQ-60: resume as soon as Wi-Fi is back
            self._log("wifi_back_resume")
            self._resume()
            return
        elapsed = self.time - self._failed_at
        if elapsed % RETRY_INTERVAL_S:
            return
        self.retry_count += 1
        if self.wifi_up:
            self._log("auto_retry_ok", attempt=self.retry_count)
            self._resume()
        else:
            self._log("auto_retry_failed", attempt=self.retry_count)
            if elapsed >= RETRY_CUTOFF_S:
                self._give_up()

    def _give_up(self) -> None:
        self._failed_at = None
        if self.offered.mandatory:
            self._log("retries_stopped_waiting_for_network")
            self._set_state(State.WAITING_FOR_NETWORK)  # REQ-32
        else:
            self.message = DOWNLOAD_FAILED_MESSAGE
            self._log("retries_stopped_user_must_retry")
            self._set_state(State.DOWNLOAD_FAILED)  # REQ-31

    def _resume(self) -> None:
        """Continue from the partial download, or restart if impossible (REQ-25)."""
        self._failed_at = None
        if self._resume_failures and self.downloaded_mb > 0:
            self._resume_failures -= 1
            self.downloaded_mb = 0.0
            self._log("download_restarted_from_zero")
        else:
            self._log("download_resumed", percent=round(self.progress_percent, 1))
        self._set_state(State.DOWNLOADING)

    def _verify(self) -> None:
        complete = self.downloaded_mb >= self.offered.size_mb
        if complete and not self._corrupt:
            self._log("verify_ok", checksum=self.offered.checksum)
            self._set_state(State.DOWNLOADED)
            return
        reason = "incomplete" if not complete else "checksum_mismatch"
        self._log("verify_rejected", reason=reason)
        self.downloaded_mb = 0.0  # rejected image is discarded, never installed
        self._failed_at = None
        self._set_state(State.VERIFY_FAILED)

    # ---------------------------------------------------------------- install
    def _tick_install(self) -> None:
        # REQ-14: installation does not depend on Wi-Fi.
        self.install_done_s += 1
        pct = 100.0 * self.install_done_s / self.install_s
        if self._fire_power_loss("install", pct):
            return
        if self.install_done_s >= self.install_s:
            self.slots[self.inactive_slot] = self.offered.version
            self._log("install_complete", slot=self.inactive_slot)
            self._set_state(State.REBOOT_PENDING)

    # ------------------------------------------------------- reboot/rollback
    def _restart(self) -> None:
        """Device comes back up after a reboot or power loss."""
        if self.state is State.REBOOT_PENDING:
            self._boot_new_firmware()
            return
        self._log("booted", slot=self.active_slot, version=self.active_version)
        if self.state in (State.DOWNLOADING, State.RETRY_WAIT):
            # REQ-61: the kept partial download (REQ-25) resumes after boot,
            # under the normal Wi-Fi rules.
            self._resume()
            if not self.wifi_up:
                self._download_failed()
        elif self.state is State.INSTALLING:
            self.slots[self.inactive_slot] = None  # half-written slot is invalid
            self._set_state(State.DOWNLOADED)
        # WAITING_FOR_NETWORK and DOWNLOAD_FAILED are kept as they were.

    def _boot_new_firmware(self) -> None:
        new_slot = self.inactive_slot
        self.failed_boots = 0
        while self.failed_boots < MAX_FAILED_BOOTS:
            reason = self._next_boot_failure()
            if reason is None:
                self.active_slot = new_slot
                self._log("booted", slot=new_slot, version=self.active_version)
                self._set_state(State.UPDATED)
                self._maybe_lose_settings("update")
                return
            self.failed_boots += 1
            self._log("boot_failed", slot=new_slot, attempt=self.failed_boots, reason=reason)
        self._log("rollback", to_slot=self.active_slot, version=self.active_version)
        self._set_state(State.ROLLED_BACK)
        self._maybe_lose_settings("rollback")

    def _next_boot_failure(self) -> str | None:
        if self._boot_power_losses:
            f = self._boot_power_losses.pop(0)
            self._power_off(f.off_s)
            return "power_loss"
        if self._boot_failures:
            self._boot_failures -= 1
            return "no_home_screen"
        return None

    def _maybe_lose_settings(self, on: str) -> None:
        if on in self._settings_lost:
            self._log("settings_lost", on=on)
            self.settings.clear()

    # ------------------------------------------------------------------ power
    def _fire_power_loss(self, stage: str, pct: float) -> bool:
        for f in self._power_losses:
            if f.stage == stage and id(f) not in self._fired and pct >= f.at_percent:
                self._fired.add(id(f))
                self._power_off(f.off_s)
                self._restart()
                return True
        return False

    def _power_off(self, off_s: int) -> None:
        self._log("power_lost", state=str(self.state))
        for _ in range(off_s):
            self.time += 1
            self._apply_wifi_schedule()
        self._log("power_restored")

    # ------------------------------------------------------------------- wifi
    def _schedule_wifi_drops(self, f: WifiDrop) -> None:
        self._set_wifi(False)
        self._wifi_schedule.append((self.time + f.duration_s, True))
        start = self.time
        for k in range(1, f.repeat):
            down_at = start + k * (f.duration_s + f.interval_s)
            self._wifi_schedule += [(down_at, False), (down_at + f.duration_s, True)]
        self._wifi_schedule.sort()

    def _apply_wifi_schedule(self) -> None:
        while self._wifi_schedule and self._wifi_schedule[0][0] <= self.time:
            _, up = self._wifi_schedule.pop(0)
            self._set_wifi(up)

    def _set_wifi(self, up: bool) -> None:
        if up == self.wifi_up:
            return
        self.wifi_up = up
        self._log("wifi_up" if up else "wifi_down")
        if not up and self.state is State.DOWNLOADING:
            self._download_failed()

    # ---------------------------------------------------------------- helpers
    def _set_state(self, state: State) -> None:
        self.state = state

    def _require(self, *allowed: State) -> None:
        if self.state not in allowed:
            names = ", ".join(s.value for s in allowed)
            raise RuntimeError(f"not allowed in state {self.state}; expected one of: {names}")

    def _log(self, name: str, **data: Any) -> None:
        self.events.append(Event(self.time, name, data))

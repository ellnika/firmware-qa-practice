# Firmware QA Practice: FW update under Wi-Fi interruption

QA practice project for over-the-air firmware updates on a streaming stick with A/B partitions. It covers what happens when Wi-Fi or power is lost during download, install or reboot.

## Contents

| Path | What it is |
|---|---|
| [requirements.md](requirements.md) | Update behavior requirements (retry rules, rollback, settings preservation), each with an ID and status |
| [fw-update-test-cases.md](fw-update-test-cases.md) | Test cases with preconditions, steps, expected results and priority (P0–P3) |
| [fwsim/](fwsim/) | A small Python simulator of the update logic, for automated tests without hardware |

## Simulator

`fwsim` simulates the device and its update logic in pure Python (3.10+, standard library only). Time is simulated, so a 6-minute Wi-Fi drop runs instantly. Failures are injected as faults.

```python
from fwsim import Simulator, FirmwareImage, WifiDrop

sim = Simulator(
    installed="1.0",
    offered=FirmwareImage("2.0", mandatory=False),
    settings={"language": "en"},
    faults=[WifiDrop(at_percent=40, duration_s=360)],
)
sim.start_download()
sim.run()

assert sim.state == "DOWNLOAD_FAILED"   # optional update: user must retry after 5 min
assert sim.active_version == "1.0"
```

**Faults:** `WifiDrop`, `PowerLoss` (download / install / boot), `CorruptImage`, `ResumeNotPossible`, `BootFailure`, `SettingsLost`.

**Actions:** `start_download()`, `retry()`, `force_verify()`, `install()`, `reboot()`, `power_cycle()`, `wifi_down()`, `wifi_restore()`, `advance(seconds)`, `run()`.

**Checks:** `state`, `active_version`, `slots`, `settings`, `retry_count`, `failed_boots`, `message`, `is_working`, `events`.

## Status

- Requirements: core rules agreed; section 7 lists default behaviors still to confirm.
- Automated pytest suite: not written yet.

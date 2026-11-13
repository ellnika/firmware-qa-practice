# Firmware QA Practice: FW update under Wi-Fi interruption

[![tests](https://github.com/ellnika/firmware-qa-practice/actions/workflows/tests.yml/badge.svg)](https://github.com/ellnika/firmware-qa-practice/actions/workflows/tests.yml)

QA practice project for over-the-air firmware updates on a streaming stick with A/B partitions. It covers what happens when Wi-Fi or power is lost during download, install or reboot.

## Contents

| Path | What it is |
|---|---|
| [requirements.md](requirements.md) | Update behavior requirements (retry rules, rollback, settings preservation), each with an ID and status |
| [fw-update-test-cases.md](fw-update-test-cases.md) | Test cases with preconditions, steps, expected results and priority (P0–P3) |
| [traceability.md](traceability.md) | Which test cases and automated tests cover each requirement, plus open points |
| [fwsim/](fwsim/) | A small Python simulator of the update logic, for automated tests without hardware |
| [demo.py](demo.py) | Runs six update scenarios on the simulator and prints what happens |
| [tests/](tests/) | Automated pytest tests against the simulator; they run on GitHub Actions for every push |

## How to run

**Requirements:** Python 3.10 or newer. Check your version with `python3 --version`.

### Run the demo

Nothing to install: the simulator uses only the standard library.

```
git clone https://github.com/ellnika/firmware-qa-practice.git
cd firmware-qa-practice
python3 demo.py
```

The demo runs six scenarios: a normal update, a brief and a long Wi-Fi drop (optional and mandatory update), a power loss during install, and a rollback after 3 failed boots. For each one it prints a timeline and the end result:

```
=== Brief Wi-Fi drop (30 s) ===
  t=  40s  wifi_down
  t=  40s  download_interrupted                 percent=40.0
  t=  70s  wifi_up
  t=  70s  wifi_back_resume
  t=  70s  download_resumed                     percent=40.0
  ...
  -> state=UPDATED, running firmware 2.0, settings={...}, working=True
```

- `t=` is **simulated** time in seconds. The whole demo finishes in under a second.
- The `->` line is where the device ended up: its state, the firmware it runs, its settings, and whether it is working.

To try your own scenario, copy a block in `demo.py` and change the faults, e.g. `WifiDrop(at_percent=80, duration_s=200)`.

### Run the automated tests

Install pytest once, in a virtual environment so your system Python stays unchanged:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Then run the tests:

```
.venv/bin/python -m pytest -v
```

Each test prints `PASSED` or `FAILED`. Each test's docstring names the test case and requirements it checks, e.g. `TC-03 | REQ-23, REQ-31`. The same tests run on GitHub Actions for every push (see the badge at the top).

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

- Requirements: 29 agreed; REQ-70 to REQ-74 (screensaver, sleep, UI, storage, playback) proposed.
- Manual test cases: 24, with P0–P3 priorities.
- Automated tests: 39 test runs against the simulator, all passing; run in CI on every push.
- Traceability and open points: [traceability.md](traceability.md).
- Defect investigation example: [docs/defect-01-retry-window.md](docs/defect-01-retry-window.md).

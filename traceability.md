# Traceability: requirements → test cases → automated tests

Links each requirement in [requirements.md](requirements.md) to the manual test cases in [fw-update-test-cases.md](fw-update-test-cases.md) and to the automated pytest tests in [tests/](tests/), which run against the [fwsim](fwsim/) simulator.

**Where a test runs**
- **Sim**: automated pytest test against the simulator.
- **Device**: manual (or later automated) test on a real Fire TV Stick.
- **Both**: automated in the simulator, then confirmed on the device. Every P0 test case is confirmed on the device.

---

## 1. Summary

| | Count |
|---|---|
| Requirements | 34 (29 Agreed, 5 Proposed) |
| Covered by a manual test case | 30 |
| Covered by an automated simulator test | 26 |
| Covered only by automated tests (no manual test case) | 2 (REQ-63, REQ-65) |
| Covered only on the device (not modelled in the simulator) | 6 (REQ-02, REQ-70 to REQ-74) |
| Not tested (environment and test method) | 2 (REQ-01, REQ-03) |
| Manual test cases | 24 (SETUP-01, TC-01 to TC-23) |
| Manual test cases with no requirement | 0 |
| Automated tests | 27 test functions, 30 test runs (with parameters), all passing |

---

## 2. Requirements → tests

| Req | Short description | Manual test cases | Automated tests | Runs on |
|---|---|---|---|---|
| REQ-01 | Fire TV Stick, A/B slots | (environment) | — | Device |
| REQ-02 | TV USB power, wall adapter as control | SETUP-01, TC-14 | — | Device |
| REQ-03 | Wi-Fi drop made at router/AP | (test method) | — | Device |
| REQ-10 | Background download, current firmware stays active | TC-01, TC-15, TC-16, TC-18, TC-19 | `test_wifi_drop_keeps_current_firmware` | Both |
| REQ-11 | Integrity check rejects bad image | TC-06 | `test_incomplete_image_rejected`, `test_corrupt_image_rejected` | Both |
| REQ-12 | Install to inactive slot, applied on reboot | TC-07, TC-08, TC-12 | `test_reboot_applies_update`, `test_power_loss_during_install_keeps_old_slot` | Both |
| REQ-13 | Never unbootable | TC-08, TC-11, TC-12, TC-13, TC-20 | `test_wifi_drop_during_reboot`, `test_power_loss_during_download_resumes`, `test_power_loss_during_install_keeps_old_slot`, `test_power_loss_during_boot_counts_as_failed_boot` | Both |
| REQ-14 | Install needs no network | TC-07 | `test_wifi_drop_during_install_no_effect` | Both |
| REQ-20 | 5-min timer starts at failure | TC-03, TC-04 | `test_retry_timing_five_retries_60s_apart`, `test_five_minute_cutoff_boundary` | Both |
| REQ-21 | Retry every 60 s | TC-03, TC-04 | `test_retry_timing_five_retries_60s_apart` | Both |
| REQ-22 | Brief drop resumes automatically | TC-02, TC-09, TC-15 | `test_brief_drop_resumes_on_reconnect`, `test_five_minute_cutoff_boundary` | Both |
| REQ-23 | Long drop, optional: manual retry | TC-03 | `test_long_drop_optional_requires_manual_retry`, `test_manual_retry_completes_download`, `test_five_minute_cutoff_boundary` | Both |
| REQ-24 | Long drop, mandatory: restarts on reconnect | TC-04 | `test_long_drop_mandatory_restarts_on_reconnect` | Both |
| REQ-25 | Resume, or restart from 0% if not possible | TC-02, TC-23 | `test_brief_drop_resumes_on_reconnect`, `test_manual_retry_completes_download`, `test_resume_not_possible_restarts_from_zero` | Both |
| REQ-30 | Never stuck in "updating" | TC-05 | `test_repeated_drops_never_stuck`, `test_long_drop_optional_requires_manual_retry`, `test_long_drop_mandatory_restarts_on_reconnect` | Both |
| REQ-31 | Optional: `DOWNLOAD_FAILED` + message | TC-03 | `test_long_drop_optional_requires_manual_retry` | Both |
| REQ-32 | Mandatory: `WAITING_FOR_NETWORK`, no message | TC-04 | `test_long_drop_mandatory_restarts_on_reconnect` | Both |
| REQ-33 | Firmware stays active, device working | TC-03, TC-04 | `test_long_drop_optional_requires_manual_retry`, `test_long_drop_mandatory_restarts_on_reconnect` | Both |
| REQ-40 | Failed boot = no home screen | TC-13, TC-20 | `test_power_loss_during_boot_counts_as_failed_boot` | Both |
| REQ-41 | Rollback after 3 failed boots | TC-20 | `test_two_failed_boots_still_updates`, `test_three_failed_boots_roll_back` | Both |
| REQ-42 | Working after rollback | TC-20 | `test_three_failed_boots_roll_back` | Both |
| REQ-50 | Settings kept after update | TC-21 | `test_settings_kept_after_update`, `test_settings_kept_after_power_loss_during_install`, `test_settings_loss_is_detected` | Both |
| REQ-51 | Settings kept after rollback | TC-22 | `test_settings_kept_after_rollback`, `test_settings_loss_is_detected` | Both |
| REQ-60 | Resume as soon as Wi-Fi returns | TC-02 | `test_brief_drop_resumes_on_reconnect` | Both |
| REQ-61 | Resume after reboot/power loss mid-download | TC-11 | `test_power_loss_during_download_resumes`, `test_reboot_while_waiting_for_network_keeps_waiting` | Both |
| REQ-62 | Each drop starts a new 5-min window | TC-05 | `test_each_drop_starts_new_retry_window` | Both |
| REQ-63 | Manual retry while offline fails once | — | `test_manual_retry_offline_fails_once` | Sim |
| REQ-64 | Rejected image is deleted, not re-downloaded | TC-06 | `test_incomplete_image_rejected` | Both |
| REQ-65 | Install is not automatic | — | `test_install_not_automatic` | Sim |
| REQ-70 *(Proposed)* | Screensaver has no effect on download | TC-09 | — | Device |
| REQ-71 *(Proposed)* | Download resumes after deep sleep | TC-10 | — | Device |
| REQ-72 *(Proposed)* | Menus and remote stay responsive | TC-16, TC-18 | — | Device |
| REQ-73 *(Proposed)* | Low storage handled cleanly | TC-17 | — | Device |
| REQ-74 *(Proposed)* | Playback works during download | TC-15, TC-19 | — | Device |

---

## 3. Test cases → requirements and automated tests

| Test case | Priority | Requirements | Automated tests | Real device needed? |
|---|---|---|---|---|
| SETUP-01 | P0 | REQ-02 | — (physical TV power) | Yes |
| TC-01 | P0 | REQ-10 | `test_wifi_drop_keeps_current_firmware` | Yes (P0) |
| TC-02 | P1 | REQ-22, REQ-25, REQ-60 | `test_brief_drop_resumes_on_reconnect`, `test_five_minute_cutoff_boundary` | Yes, once (real Wi-Fi timing) |
| TC-03 | P1 | REQ-20, REQ-21, REQ-23, REQ-31, REQ-33 | `test_long_drop_optional_requires_manual_retry`, `test_manual_retry_completes_download`, `test_retry_timing_five_retries_60s_apart`, `test_five_minute_cutoff_boundary` | Yes, once |
| TC-04 | P1 | REQ-20, REQ-21, REQ-24, REQ-32, REQ-33 | `test_long_drop_mandatory_restarts_on_reconnect`, `test_retry_timing_five_retries_60s_apart` | Yes, once |
| TC-05 | P2 | REQ-30, REQ-62 | `test_repeated_drops_never_stuck`, `test_each_drop_starts_new_retry_window` | Yes, once |
| TC-06 | P0 | REQ-11, REQ-64 | `test_incomplete_image_rejected`, `test_corrupt_image_rejected` | Yes (real signature check) |
| TC-07 | P0 | REQ-12, REQ-14 | `test_wifi_drop_during_install_no_effect` | Yes (real flash) |
| TC-08 | P0 | REQ-12, REQ-13 | `test_reboot_applies_update`, `test_wifi_drop_during_reboot` | Yes (real bootloader) |
| TC-09 | P3 | REQ-22, REQ-70 | — (screensaver not modelled) | Yes |
| TC-10 | P2 | REQ-71 | — (deep sleep not modelled) | Yes |
| TC-11 | P2 | REQ-02, REQ-13, REQ-61 | `test_power_loss_during_download_resumes` | Yes (TV power) |
| TC-12 | P0 | REQ-12, REQ-13 | `test_power_loss_during_install_keeps_old_slot`, `test_settings_kept_after_power_loss_during_install` | Yes (TV power, real flash) |
| TC-13 | P0 | REQ-13, REQ-40 | `test_power_loss_during_boot_counts_as_failed_boot` | Yes (TV power, real bootloader) |
| TC-14 | P2 | REQ-02 | — (power source not modelled) | Yes |
| TC-15 | P2 | REQ-10, REQ-22, REQ-74 | Partly: download side by `test_brief_drop_resumes_on_reconnect`; playback not modelled | Yes |
| TC-16 | P3 | REQ-10, REQ-72 | — (UI not modelled) | Yes |
| TC-17 | P2 | REQ-73 | — (storage not modelled) | Yes |
| TC-18 | P3 | REQ-10, REQ-72 | — (UI not modelled) | Yes |
| TC-19 | P3 | REQ-10, REQ-74 | — (playback not modelled) | Yes |
| TC-20 | P0 | REQ-13, REQ-40, REQ-41, REQ-42 | `test_three_failed_boots_roll_back`, `test_two_failed_boots_still_updates` | Yes (real bootloader, broken test build) |
| TC-21 | P1 | REQ-50 | `test_settings_kept_after_update` | Yes |
| TC-22 | P1 | REQ-51 | `test_settings_kept_after_rollback` | Yes |
| TC-23 | P2 | REQ-25 | `test_resume_not_possible_restarts_from_zero` | Yes (needs server access) |

---

## 4. Automated tests

Run with `python -m pytest -v` (see [README](README.md#run-the-automated-tests)). They also run on GitHub Actions for every push ([.github/workflows/tests.yml](.github/workflows/tests.yml)).

| File | Tests | Covers |
|---|---|---|
| [tests/test_download.py](tests/test_download.py) | 13 functions (15 runs) | Wi-Fi drops, retry timing and the 5-minute boundary, manual retry, mandatory updates, resume vs restart, power loss mid-download |
| [tests/test_verify_install.py](tests/test_verify_install.py) | 5 | Integrity check, install without Wi-Fi, power loss during install, install not automatic |
| [tests/test_boot_rollback.py](tests/test_boot_rollback.py) | 5 | Reboot into 2.0, power loss during boot, 2 vs 3 failed boots, rollback |
| [tests/test_settings.py](tests/test_settings.py) | 4 functions (5 runs) | Settings after update, rollback and power loss; a check that a lost setting is really detected |

Each test's docstring names its test case and requirements, e.g. `"""TC-03 | REQ-23, REQ-31"""`.

---

## 5. Open points

| Item | Note |
|---|---|
| REQ-70 to REQ-74 | **Proposed**, waiting for confirmation. Device-only: the simulator does not model the screensaver, sleep, storage, UI or playback. |
| Exactly 5-minute drop | TC-02 and TC-03 say "< 5 min" and "> 5 min". The tests define the boundary: Wi-Fi back at exactly 5:00 counts as a brief drop (`test_five_minute_cutoff_boundary`). Confirm this with the team. |
| TC-20, TC-22 | Need a deliberately broken 2.0 test build that cannot reach the home screen. |
| TC-23 | Needs a way to publish a new image on the update server during the test. |
| Device automation | All device tests are manual. The same test cases could later be automated on the device, e.g. through ADB. |

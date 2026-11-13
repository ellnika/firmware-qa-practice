# Traceability: requirements → test cases → planned tests

Links each requirement in [requirements.md](requirements.md) to the manual test cases in [fw-update-test-cases.md](fw-update-test-cases.md) and to the planned automated (pytest) tests against the [fwsim](fwsim/) simulator. It also lists the gaps and review findings.

**Status:** planned. The pytest tests listed here are not written yet.

**Where a test runs**
- **Sim**: automated pytest test against the simulator.
- **Device**: manual (or later automated) test on a real Fire TV Stick.
- **Both**: automated in the simulator first, then confirmed on the device. Every P0 test case is confirmed on the device.

---

## 1. Summary

| | Count |
|---|---|
| Requirements | 29 (23 Agreed, 6 Proposed) |
| Requirements covered by at least one manual test case | 21 (4 of them only partly: REQ-20, REQ-21, REQ-25, REQ-31) |
| Requirements covered only by a planned simulator test (no manual test case) | 6 (REQ-41, REQ-42, REQ-50, REQ-51, REQ-63, REQ-65) |
| Requirements with no test (environment setup only) | 2 (REQ-01, REQ-03) |
| Manual test cases with no matching requirement | 6 (TC-09, TC-10, TC-16, TC-17, TC-18, TC-19) |
| Planned simulator tests | 24 |

---

## 2. Requirements → tests

| Req | Short description | Manual test cases | Planned pytest test(s) | Runs on |
|---|---|---|---|---|
| REQ-01 | Fire TV Stick, A/B slots | (environment) | — | Device |
| REQ-02 | TV USB power, wall adapter as control | SETUP-01, TC-14 | — | Device |
| REQ-03 | Wi-Fi drop made at router/AP | (test method) | — | Device |
| REQ-10 | Background download, current firmware stays active | TC-01, TC-15, TC-16, TC-18, TC-19 | `test_wifi_drop_keeps_current_firmware` | Both |
| REQ-11 | Integrity check rejects bad image | TC-06 | `test_incomplete_image_rejected`, `test_corrupt_image_rejected` | Both |
| REQ-12 | Install to inactive slot, applied on reboot | TC-07, TC-12 | `test_reboot_applies_update` | Both |
| REQ-13 | Never unbootable | TC-08, TC-11, TC-12, TC-13 | `test_power_loss_during_download_resumes`, `test_power_loss_during_install_keeps_old_slot`, `test_wifi_drop_during_reboot` | Both |
| REQ-14 | Install needs no network | TC-07 | `test_wifi_drop_during_install_no_effect` | Both |
| REQ-20 | 5-min timer starts at failure | TC-03, TC-04 (indirectly) | `test_retry_timing_five_retries_60s_apart` | Sim |
| REQ-21 | Retry every 60 s | TC-03, TC-04 (indirectly) | `test_retry_timing_five_retries_60s_apart` | Sim |
| REQ-22 | Brief drop resumes automatically | TC-02, TC-09, TC-15 | `test_brief_drop_resumes_on_reconnect` | Both |
| REQ-23 | Long drop, optional: manual retry | TC-03 | `test_long_drop_optional_requires_manual_retry`, `test_manual_retry_completes_download` | Both |
| REQ-24 | Long drop, mandatory: restarts on reconnect | TC-04 | `test_long_drop_mandatory_restarts_on_reconnect` | Both |
| REQ-25 | Resume, or restart from 0% if not possible | TC-02 (resume only) | `test_brief_drop_resumes_on_reconnect`, `test_resume_not_possible_restarts_from_zero` | Sim |
| REQ-30 | Never stuck in "updating" | TC-05 | `test_repeated_drops_never_stuck` | Both |
| REQ-31 | Optional: `DOWNLOAD_FAILED` + message | TC-03 (partial: message not checked) | `test_long_drop_optional_requires_manual_retry` | Both |
| REQ-32 | Mandatory: `WAITING_FOR_NETWORK`, no message | TC-04 | `test_long_drop_mandatory_restarts_on_reconnect` | Both |
| REQ-33 | Firmware stays active, device working | TC-03, TC-04 | `test_long_drop_optional_requires_manual_retry`, `test_long_drop_mandatory_restarts_on_reconnect` | Both |
| REQ-40 | Failed boot = no home screen | TC-13 | `test_power_loss_during_boot_counts_as_failed_boot` | Both |
| REQ-41 | Rollback after 3 failed boots | — | `test_two_failed_boots_still_updates`, `test_three_failed_boots_roll_back` | Sim |
| REQ-42 | Working after rollback | — | `test_three_failed_boots_roll_back` | Sim |
| REQ-50 | Settings kept after update | — | `test_settings_kept_after_update`, `test_settings_loss_is_detected` | Sim |
| REQ-51 | Settings kept after rollback | — | `test_settings_kept_after_rollback`, `test_settings_loss_is_detected` | Sim |
| REQ-60 *(Proposed)* | Resume as soon as Wi-Fi returns | TC-02 | `test_brief_drop_resumes_on_reconnect` | Both |
| REQ-61 *(Proposed)* | Resume after reboot/power loss mid-download | TC-11 | `test_power_loss_during_download_resumes` | Both |
| REQ-62 *(Proposed)* | Each drop starts a new 5-min window | TC-05 | `test_repeated_drops_never_stuck` | Sim |
| REQ-63 *(Proposed)* | Manual retry while offline fails once | — | `test_manual_retry_offline_fails_once` | Sim |
| REQ-64 *(Proposed)* | Rejected image is deleted, not re-downloaded | TC-06 | `test_incomplete_image_rejected` | Sim |
| REQ-65 *(Proposed)* | Install is not automatic | — | `test_install_not_automatic` | Sim |

---

## 3. Test cases → requirements

| Test case | Priority | Requirements | Simulator test? | Real device needed? |
|---|---|---|---|---|
| SETUP-01 | P0 | REQ-02 | No (physical TV power) | Yes |
| TC-01 | P0 | REQ-10 | Yes | Yes (P0) |
| TC-02 | P1 | REQ-22, REQ-25, REQ-60 | Yes | Yes, once (real Wi-Fi timing) |
| TC-03 | P1 | REQ-20, REQ-21, REQ-23, REQ-31, REQ-33 | Yes | Yes, once |
| TC-04 | P1 | REQ-24, REQ-32, REQ-33 | Yes | Yes, once |
| TC-05 | P2 | REQ-30, REQ-62 | Yes | Yes, once |
| TC-06 | P0 | REQ-11, REQ-64 | Yes | Yes (real signature check) |
| TC-07 | P0 | REQ-12, REQ-14 | Yes | Yes (real flash) |
| TC-08 | P0 | REQ-13 | Yes | Yes (real bootloader) |
| TC-09 | P3 | REQ-22 only (screensaver not specified) | No (not modelled) | Yes |
| TC-10 | P2 | None (deep sleep not specified) | No (not modelled) | Yes |
| TC-11 | P2 | REQ-02, REQ-13, REQ-61 | Yes | Yes (TV power) |
| TC-12 | P0 | REQ-12, REQ-13 | Yes | Yes (TV power, real flash) |
| TC-13 | P0 | REQ-13, REQ-40, REQ-41 | Yes | Yes (TV power, real bootloader) |
| TC-14 | P2 | REQ-02 | No (power source not modelled) | Yes |
| TC-15 | P2 | REQ-10, REQ-22 | Partly (download only, not playback) | Yes |
| TC-16 | P3 | REQ-10 only (menu responsiveness not specified) | No (UI not modelled) | Yes |
| TC-17 | P2 | None (low storage not specified) | No (not modelled) | Yes |
| TC-18 | P3 | REQ-10 only (remote input not specified) | No (UI not modelled) | Yes |
| TC-19 | P3 | REQ-10 only (playback not specified) | No (UI not modelled) | Yes |

---

## 4. Planned pytest tests

Planned layout under `tests/`. Each test uses the simulator only and maps to the requirements above.

| File | Test | Test case | Requirements |
|---|---|---|---|
| `test_download.py` | `test_wifi_drop_keeps_current_firmware` | TC-01 | REQ-10 |
| | `test_brief_drop_resumes_on_reconnect` | TC-02 | REQ-22, REQ-25, REQ-60 |
| | `test_long_drop_optional_requires_manual_retry` | TC-03 | REQ-23, REQ-31, REQ-33 |
| | `test_manual_retry_completes_download` | TC-03 | REQ-23 |
| | `test_manual_retry_offline_fails_once` | — | REQ-63 |
| | `test_retry_timing_five_retries_60s_apart` | TC-03, TC-04 | REQ-20, REQ-21 |
| | `test_long_drop_mandatory_restarts_on_reconnect` | TC-04 | REQ-24, REQ-32, REQ-33 |
| | `test_repeated_drops_never_stuck` | TC-05 | REQ-30, REQ-62 |
| | `test_resume_not_possible_restarts_from_zero` | — | REQ-25 |
| | `test_power_loss_during_download_resumes` | TC-11 | REQ-13, REQ-61 |
| `test_verify_install.py` | `test_incomplete_image_rejected` | TC-06 | REQ-11, REQ-64 |
| | `test_corrupt_image_rejected` | TC-06 | REQ-11 |
| | `test_wifi_drop_during_install_no_effect` | TC-07 | REQ-14 |
| | `test_power_loss_during_install_keeps_old_slot` | TC-12 | REQ-12, REQ-13 |
| | `test_install_not_automatic` | — | REQ-65 |
| `test_boot_rollback.py` | `test_reboot_applies_update` | TC-08 | REQ-12 |
| | `test_wifi_drop_during_reboot` | TC-08 | REQ-13 |
| | `test_power_loss_during_boot_counts_as_failed_boot` | TC-13 | REQ-40 |
| | `test_two_failed_boots_still_updates` | — | REQ-41 (boundary) |
| | `test_three_failed_boots_roll_back` | — | REQ-41, REQ-42 |
| `test_settings.py` | `test_settings_kept_after_update` | — | REQ-50 |
| | `test_settings_kept_after_rollback` | — | REQ-51 |
| | `test_settings_loss_is_detected` | — | REQ-50, REQ-51 (checks the test catches a real loss, using the `SettingsLost` fault) |
| | `test_settings_kept_after_power_loss_during_install` | TC-12 | REQ-13, REQ-50 |

---

## 5. Gaps and review findings

These are listed for decision. No requirement or test case has been changed because of them.

### Requirements with no manual test case

| Requirement | Gap | Suggestion |
|---|---|---|
| REQ-41, REQ-42 | No test case forces a rollback (3 failed boots). TC-08 and TC-13 accept "boots 2.0 **or** rolls back", so rollback may never be exercised. | Add a test case that makes the new firmware fail to boot (e.g. a deliberately broken test build). |
| REQ-50, REQ-51 | No test case checks settings preservation, although it is a project goal. | Add test cases: settings kept after update, and after rollback. |
| REQ-25 | Only "resume" is tested; "restart from 0% when resume is not possible" is not. | Add a test case, e.g. new image published on the server mid-download. |
| REQ-20, REQ-21 | No test case checks the exact retry timing (every 60 s, stop at 5 min). | Add timing checks to TC-03/TC-04, or cover in the simulator only. |
| REQ-31 | TC-03 does not check the message text or the Retry button. | Add the message to TC-03's expected results. |
| REQ-63, REQ-65 | Proposed defaults with no test case. | Confirm the requirements first. |

### Test cases with no requirement

TC-09 (screensaver), TC-10 (deep sleep), TC-16 (menus), TC-17 (low storage), TC-18 (remote input) and TC-19 (playback after Wi-Fi returns) test behavior that [requirements.md](requirements.md) does not define. Their expected results cannot be traced to an agreed rule. **Suggestion:** add requirements for these areas, or mark the test cases as exploratory.

### Inconsistencies

| Where | Issue |
|---|---|
| [fw-update-test-cases.md](fw-update-test-cases.md), Baseline assumptions | Still says "Retry policy: 10 retries x 60 s". REQ-21 replaced this with "every 60 s, for at most 5 minutes" (see requirements.md §10). |
| TC-02 and TC-03 | Say "< 5 min" / "> 5 min" drop; a drop of exactly 5 min is not defined. The simulator treats Wi-Fi back at exactly 5:00 as a brief drop (it is back for the 5th retry). |
| REQ-60–REQ-65 | Still **Proposed**. Tests built on them may need changes if they are not confirmed. |

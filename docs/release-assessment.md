# Release assessment: firmware update logic 1.0 → 2.0

| | |
|---|---|
| Scope | Over-the-air update logic under Wi-Fi and power interruption: download, retry, verify, install to the inactive slot, reboot, rollback, settings |
| Tested on | `fwsim` simulator only; no device results are included in this repo |
| Date | 2026-11-14 |
| Recommendation | **Ready for device testing. Not a release sign-off.** |

## 1. Evidence

| Check | Result |
|---|---|
| Automated tests | 32 test functions, 39 runs, all passing |
| Fresh clone | Cloned from GitHub into an empty folder and followed the README exactly: demo runs, 39 passed |
| CI | GitHub Actions on every push and pull request, Python 3.10 and 3.12, green on `main` |
| Requirements covered | 35 requirements: 26 by automated simulator tests, 6 only on the device, 2 not testable (environment and test method), 1 proposed and not yet covered (REQ-66). See [traceability.md](../traceability.md) |
| Manual test cases | 24 (SETUP-01, TC-01 to TC-23), each linked to a requirement |
| Tests catch defects | The end-to-end, boundary and retry-window tests were each run against a planted defect and failed as expected |

## 2. Defects found

| ID | What | Found by | Status |
|---|---|---|---|
| Simulator bug | After a repeated Wi-Fi drop, the first retry was counted immediately instead of 60 s later, so some scenarios showed 6 retries instead of 5 (REQ-21) | Scenario review during development | Fixed in [3e941a6](https://github.com/ellnika/firmware-qa-practice/commit/3e941a66d136455f81cc417b8f91ed012e2be1c8) |
| Test case error | The old baseline in the manual test cases said "10 retries", which contradicts the 5-minute / 60 s rule (REQ-20, REQ-21) | Requirements review | Fixed in [b2350f1](https://github.com/ellnika/firmware-qa-practice/commit/b2350f1a536ad14e2d7fd1a539db645e94bf2562) |
| Defect 01 (seeded) | A new Wi-Fi drop didn't start a new 5-minute window (REQ-62) | `test_each_drop_starts_new_retry_window`, local and CI | Fixed; also closed a test gap. [Report](defect-01-retry-window.md) |

## 3. Open risks

| Risk | Impact | Needed before release |
|---|---|---|
| P0 cases not yet confirmed on a device: SETUP-01, TC-01, TC-06, TC-07, TC-08, TC-12, TC-13, TC-20 | The simulator models the rules, not the real flash, bootloader or Wi-Fi stack | Run all P0 cases on a real device. Any P0 failure blocks the release |
| Exactly 5:00 drop counts as brief (auto-resume) | Tests encode an assumption the spec doesn't state | Team confirms the boundary |
| No overall download time limit (proposed REQ-66) | A connection that keeps dropping for less than 5 min at a time could keep a download going indefinitely | Team agrees the limit and the mandatory-update behavior; then add a test |
| REQ-70 to REQ-74 (screensaver, sleep, UI, storage, playback) still proposed | Behaviour in these states is undefined | Agree the requirements, then run TC-09, TC-10, TC-15 to TC-19 on the device |
| TC-20, TC-22 need a deliberately broken 2.0 build | Rollback can't be shown on a device without it | Build team provides a test build |
| TC-23 needs a way to publish a new image during a test | Restart-from-0% can't be shown on a device | Update-server hook or test server |

## 4. Recommendation

The update logic behaves as specified in every simulated scenario, including the boundaries, and the tests catch real defects. That makes it ready for **device testing**.

It is **not ready for release** until all P0 cases pass on a real device and the 5:00 boundary is confirmed. Those cases decide whether a device can be left unbootable, which the simulator cannot prove.

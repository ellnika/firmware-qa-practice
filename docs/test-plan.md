# Test plan: firmware update under Wi-Fi and power interruption

| | |
|---|---|
| Product | Over-the-air firmware update, 1.0 → 2.0, on a streaming stick with A/B slots |
| Version | 1.0, 2026-11-14 |
| Test owner | Ewa (approved 2026-11-16) |
| Status | Simulator phase complete; device phase not started |

> **Note:** this plan was written after the simulator phase, to record the scope, approach and criteria the work followed and to set them for the device phase. Results so far are in the [release assessment](release-assessment.md).

---

## 1. Goal

Show that a firmware update can be interrupted at any stage, by Wi-Fi loss or power loss, without ever leaving the device unbootable, losing user settings, or leaving the user stuck. Decide whether the update is ready for release.

## 2. Scope

**In scope**

| Area | Requirements |
|---|---|
| Background download and integrity check | REQ-10, REQ-11, REQ-64 |
| Wi-Fi drop during download: retry timing, 5-minute cutoff, resume vs restart | REQ-20 to REQ-25, REQ-60 to REQ-63 |
| State after retries stop, optional vs mandatory update | REQ-30 to REQ-33 |
| Install to the inactive slot, reboot, never unbootable | REQ-12 to REQ-14, REQ-65 |
| Power loss during download, install and boot | REQ-13, REQ-61 |
| Rollback after failed boots | REQ-40 to REQ-42 |
| Settings kept after update and rollback | REQ-50, REQ-51 |
| Device behavior during an update (device only) | REQ-70 to REQ-74 (proposed) |

**Out of scope**

- The update server, image signing and security of the update channel.
- Download speed and performance; real-world network conditions beyond on/off Wi-Fi.
- Updates other than 1.0 → 2.0, such as downgrades or skipped versions.
- Other devices and power setups beyond TV USB power and the wall-adapter control.

## 3. Risks and priorities

Testing effort follows product risk. The worst outcome for the user decides the priority ([priority levels](../fw-update-test-cases.md#priority-levels)).

| Risk | Worst outcome | Priority | Covered by |
|---|---|---|---|
| Interruption during install or boot | Device unbootable ("bricked") | P0 | TC-07, TC-08, TC-12, TC-13, TC-20 |
| Incomplete or corrupt image accepted | Broken firmware installed | P0 | TC-06 |
| Firmware switches before reboot | Unexpected change for the user | P0 | TC-01, TC-08 |
| Retry and cutoff rules wrong | Update gives up too early, or never | P1 | TC-02 to TC-04 |
| Settings lost | User has to set up the device again | P1 | TC-21, TC-22 |
| Stuck in "updating" or retrying forever | Update never finishes | P1–P2 | TC-05, REQ-66 (proposed) |
| Download disturbs normal use | Playback, menus or remote affected | P2–P3 | TC-09, TC-10, TC-15 to TC-19 |

## 4. Approach

Two phases, using the same requirements and test cases.

**Phase 1: simulator (automated).** A Python simulator (`fwsim`) models the update rules with simulated time and injected faults. pytest tests check it on every push in GitHub Actions. This finds logic errors quickly and repeatably, before any device is involved.

**Phase 2: device (manual).** The same test cases run on a real Fire TV Stick, to confirm what the simulator cannot: the real flash, bootloader, signature check and Wi-Fi stack. Every P0 case must be run on the device.

**Test techniques**

| Technique | Where it is used |
|---|---|
| Boundary values | Wi-Fi drop of 299 / 300 / 301 s around the 5-minute cutoff, for optional and mandatory updates; 2 vs 3 failed boots |
| State transitions | Every update state (downloading, retry wait, failed, installed, updated, rolled back) and the events between them |
| Fault injection | Wi-Fi drops, power loss at each stage, corrupt image, resume not possible, failed boots, lost settings |
| Equivalence classes | Optional vs mandatory update; brief vs long drop |
| Negative tests | Corrupt image, manual retry while offline, install not starting by itself |
| Checking the tests | Each new test must fail when a matching defect is planted; a test that cannot fail does not count |

**Traceability.** Every requirement maps to test cases and automated tests in [traceability.md](../traceability.md). A requirement without a test is listed as a gap.

## 5. Environments

| Phase | Environment |
|---|---|
| Simulator | Python 3.10 and 3.12; pytest 8.3.3; GitHub Actions (Ubuntu) on every push and pull request; local runs from a fresh clone |
| Device | Fire TV Stick with A/B slots, powered from the TV's USB port, with a wall adapter as control (REQ-01, REQ-02). Wi-Fi drops made at the router/AP (REQ-03). Version check through Settings > About and ADB. Needs a broken 2.0 test build (TC-20, TC-22) and a way to publish a new image during a test (TC-23) |

## 6. Entry and exit criteria

| Phase | Entry | Exit |
|---|---|---|
| Simulator | Requirements written; simulator runs | All automated tests pass locally and in CI. Every agreed requirement is traced to a test or a justified device-only/manual case. Each new test has failed on a planted defect |
| Device | Simulator phase exited; device and test builds available; SETUP-01 done | All P0 cases pass. No open P0 or P1 defects |
| Release | Device phase exited | 5:00 boundary and REQ-66 decided by the team. Release assessment signed off by the test owner |

## 7. Defect handling

- Each defect gets a report with: failing test, evidence (test output, event log), root cause, fix, verification, and severity. Example: [defect 01](defect-01-retry-window.md).
- Severity follows the priority levels: P0 blocks the release.
- Fixes go through a branch and a pull request, so CI shows red with the defect and green with the fix before merging.
- If investigating a defect shows a gap in the tests or requirements, it is added: a new test, or a proposed requirement (for example REQ-66).

## 8. Roles and use of AI

| Role | Who | Responsibilities |
|---|---|---|
| Test owner | Ewa | Owns this plan: scope, priorities, entry and exit criteria. Reviews and approves AI output before it is committed. Decides severity and the release recommendation. Raises gaps in the requirements |
| Planning assistant | ChatGPT | Proposed the project idea, milestones and task breakdown |
| Implementation assistant | Claude Code | Writes the simulator, tests, CI and documents; investigates failures; posts evidence on the task board |

**Rules for AI output**
- Nothing counts as done until the test owner has reviewed it.
- A test must assert what its requirement means, not only pass, and must fail on a planted defect.
- AI findings in a defect investigation are checked against the actual test output and logs.
- No claims of device validation from simulator results.

## 9. Deliverables

| Deliverable | Link |
|---|---|
| Requirements | [requirements.md](../requirements.md) |
| Test cases | [fw-update-test-cases.md](../fw-update-test-cases.md) |
| Traceability matrix and open points | [traceability.md](../traceability.md) |
| Simulator and automated tests | [fwsim/](../fwsim/), [tests/](../tests/) |
| CI pipeline | [.github/workflows/tests.yml](../.github/workflows/tests.yml) |
| Defect report | [defect-01-retry-window.md](defect-01-retry-window.md) |
| Release assessment | [release-assessment.md](release-assessment.md) |

## 10. Schedule

| Target | Milestone | Actual |
|---|---|---|
| Nov 15 | Simulator runs; requirements, test cases, traceability | Done Nov 13 |
| Nov 17 | Success-path automation | Done Nov 13 |
| Nov 19 | Recovery and negative tests | Done Nov 13 |
| Nov 21 | Defect detection and investigation | Done Nov 13 |
| Nov 23 | CI pipeline, failure shown to block | Done Nov 13 |
| Nov 25 | Release assessment and documentation | In progress |
| Not scheduled | Device phase | Not started |

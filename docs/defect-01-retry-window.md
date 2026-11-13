# Defect 01: Retry window not reset on a new Wi-Fi drop

| | |
|---|---|
| Status | Fixed; merged to `main` in [PR #1](https://github.com/ellnika/firmware-qa-practice/pull/1) |
| Type | Seeded on purpose, to check that the tests and CI catch a realistic defect |
| Requirement broken | REQ-62 (each drop starts a new 5-minute window), and as a side effect REQ-21 (retry every 60 s) |
| Severity | High: an optional update gives up and shows the error message after a short outage |
| Found by | `test_each_drop_starts_new_retry_window`, local run and GitHub Actions |
| Defect commit | [f6909f6](https://github.com/ellnika/firmware-qa-practice/commit/f6909f6feac2b199899fe3b832bcfca0524593f5) |
| Failing CI run | [run 43479877548](https://github.com/ellnika/firmware-qa-practice/actions/runs/43479877548): "Run tests" failed on Python 3.10; the 3.12 job was cancelled by GitHub's fail-fast default |

## 1. The change that caused it

A developer "optimised" the retry timer so a resume would not reset it:

```diff
     def _download_failed(self) -> None:
-        self._failed_at = self.time  # REQ-20: timer starts at the failure
+        # Keep the original failure time so a resume doesn't reset the timer.
+        if self._failed_at is None:
+            self._failed_at = self.time  # REQ-20: timer starts at the failure
...
     def _resume(self) -> None:
-        self._failed_at = None
```

## 2. Failing test

```
FAILED tests/test_download.py::test_each_drop_starts_new_retry_window
E       AssertionError: assert 2 == 4
E        +  where 2 = len([Event(t=20, name='wifi_down'), Event(t=270, name='wifi_down')])
        events(<Simulator t=320s state=DOWNLOAD_FAILED active=1.0 progress=29% wifi=down>, 'wifi_down')
1 failed, 37 passed
```

The test makes four Wi-Fi drops of 4 minutes each, 10 s apart. Every drop is shorter than 5 minutes, so the download should never give up. With the defect, it stopped after the second drop, in state `DOWNLOAD_FAILED`.

## 3. Investigation from the event log

Same scenario (optional update, Wi-Fi drops at 20%, 4 × 240 s, 10 s apart), first 13 events:

| t (s) | With defect | Expected (main) |
|---|---|---|
| 20 | `wifi_down`, `download_interrupted` 20% | same |
| 80, 140, 200 | `auto_retry_failed` 1, 2, 3 | same |
| 260 | `wifi_up`, `download_resumed` 20% | same |
| 270 | `wifi_down`, `download_interrupted` 29% | same |
| **320** | **`auto_retry_failed` 1, `retries_stopped_user_must_retry`** | (nothing) |
| 330 | — | `auto_retry_failed` 1 |
| … | — | 2 more drops, each recovers; `download_complete` at 1063 |

What the log shows:

1. After the second drop at t=270, the first retry came at **t=320, 50 s later** instead of 60 s. Retries were still timed from the **first** drop at t=20 (20 + 300 = 320).
2. At t=320 the device decided the 5-minute window was over, **300 s after the first drop but only 50 s after the second**, and gave up with the error message.
3. So the failure time `_failed_at` was not reset when the download resumed. That pointed straight at `_download_failed` and `_resume`, the two places that set it.

Root cause: `_resume()` no longer clears `_failed_at`, and `_download_failed()` only sets it when it is empty. Every drop after the first inherits the first drop's start time.

## 4. Test gap found

Only one test failed, but the log showed a second symptom: the 60 s retry spacing (REQ-21) was wrong after the second drop. `test_retry_timing_five_retries_60s_apart` covers a single drop only, so nothing checked this.

Added `test_retries_60s_after_each_drop`: two drops, and the first retry after each must be exactly 60 s later. With the defect it fails with `assert [60, 50] == [60, 60]`; with the fix it passes.

## 5. Fix and verification

- Fix: restore the original lines, so every new drop sets `_failed_at` to its own time and every resume clears it.
- Local run after the fix: 39 passed (38 before + the new test).
- CI after the fix: [run 43480166783](https://github.com/ellnika/firmware-qa-practice/actions/runs/43480166783) (branch), [run 43500916693](https://github.com/ellnika/firmware-qa-practice/actions/runs/43500916693) (pull request), [run 43500962341](https://github.com/ellnika/firmware-qa-practice/actions/runs/43500962341) (`main` after merge), all green.

## 6. AI and human contribution

- Claude Code seeded the defect, ran the tests, compared the event logs and drafted this report.
- Each claim above was checked against the actual test output and event log printed during the investigation.
- Review by Ewa: _pending_ (confirm the root cause, the severity, and that the new test checks what REQ-21 and REQ-62 mean).

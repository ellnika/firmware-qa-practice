# FW Update AI Pilot — Baseline Test Cases (Wi-Fi interruption)

## Contents

| ID | Priority | Scenario |
|---|---|---|
| [SETUP-01](#setup-01-confirm-tv-usb-power-behavior) | P0 | Confirm TV USB power behavior |
| [TC-01](#tc-01-wi-fi-drops-during-a-firmware-download) | P0 | Wi-Fi drops during a firmware download |
| [TC-02](#tc-02-brief-wi-fi-drop--5-min-during-download-optional-update) | P1 | Brief Wi-Fi drop (< 5 min) during download, optional update |
| [TC-03](#tc-03-long-wi-fi-drop--5-min-during-download-optional-update) | P1 | Long Wi-Fi drop (> 5 min) during download, optional update |
| [TC-04](#tc-04-long-wi-fi-drop--5-min-during-download-mandatory-update) | P1 | Long Wi-Fi drop (> 5 min) during download, mandatory update |
| [TC-05](#tc-05-repeated-wi-fi-drops-during-download) | P2 | Repeated Wi-Fi drops during download |
| [TC-06](#tc-06-partial-download-fails-integrity-check) | P0 | Partial download fails integrity check |
| [TC-07](#tc-07-wi-fi-drop-during-install-to-inactive-slot) | P0 | Wi-Fi drop during install to inactive slot |
| [TC-08](#tc-08-wi-fi-drop-during-reboot-into-20) | P0 | Wi-Fi drop during reboot into 2.0 |
| [TC-09](#tc-09-wi-fi-drop-while-device-is-in-screensaver) | P3 | Wi-Fi drop while device is in screensaver |
| [TC-10](#tc-10-wi-fi-drop-while-device-is-in-deep-sleep) | P2 | Wi-Fi drop while device is in deep sleep |
| [TC-11](#tc-11-tv-off-usb-power-cut-during-download) | P2 | TV off (USB power cut) during download |
| [TC-12](#tc-12-tv-off-usb-power-cut-during-install-to-inactive-slot) | P0 | TV off (USB power cut) during install to inactive slot |
| [TC-13](#tc-13-tv-off-usb-power-cut-during-reboot-into-20) | P0 | TV off (USB power cut) during reboot into 2.0 |
| [TC-14](#tc-14-control-wi-fi-drop-during-download-on-wall-power) | P2 | Control: Wi-Fi drop during download on wall power |
| [TC-15](#tc-15-wi-fi-drop-during-download-while-streaming) | P2 | Wi-Fi drop during download while streaming |
| [TC-16](#tc-16-wi-fi-drop-during-download-while-in-a-menu) | P3 | Wi-Fi drop during download while in a menu |
| [TC-17](#tc-17-wi-fi-drop-during-download-with-low-storage) | P2 | Wi-Fi drop during download with low storage |
| [TC-18](#tc-18-user-presses-remote-buttons-during-wi-fi-drop) | P3 | User presses remote buttons during Wi-Fi drop |
| [TC-19](#tc-19-user-starts-playback-right-after-wi-fi-returns) | P3 | User starts playback right after Wi-Fi returns |

---

## Baseline assumptions
- Device: Fire TV Stick, A/B partitions, powered from TV USB port (wall adapter as control).
- Update downloads in the background, is integrity-checked (hash/signature), and applies on reboot.
- Brief drop (< 5 min): download resumes automatically. Drop > 5 min: user must retry manually, unless the update is mandatory (then retries automatically). Retry policy: 10 retries x 60 s; the 5-minute cutoff takes precedence.
- Wi-Fi drop is simulated at the router/AP (AP off or device blocked).
- **"Device is working"** = boots to home screen, connects to Wi-Fi, plays content, remote responds.
- **Version check** = Settings > About, plus ADB where available.

## Priority levels
- **P0 (Blocker)**: A failure could leave the device unbootable, install a corrupt image, or switch firmware unexpectedly. Release cannot ship.
- **P1 (Critical)**: Core update rules (auto-resume, 5-minute cutoff, manual retry, mandatory retry) do not work as specified.
- **P2**: Important secondary behavior (retry robustness, sleep, storage, power-source control).
- **P3**: User-experience checks while an update is in progress.

---

## Setup checks

### SETUP-01: Confirm TV USB power behavior

**Priority: P0**

**Preconditions**

- Device connected to TV USB port

**Steps**

1. Turn TV off.
2. Check whether the device loses power (LED off / ADB disconnects).

**Expected results**

- Result recorded; determines whether TV-off tests (TC-11–TC-13) represent power loss.

---

## Test cases

### TC-01: Wi-Fi drops during a firmware download

**Priority: P0**

**Preconditions**

- Device is running firmware 1.0

**Steps**

1. Start downloading firmware 2.0.
2. Interrupt Wi-Fi partway through the download.

**Expected results**

- Firmware 1.0 is still active after the interruption.

---

### TC-02: Brief Wi-Fi drop (< 5 min) during download, optional update

**Priority: P1**

**Preconditions**

- Device on 1.0, idle on home screen; optional 2.0 available

**Steps**

1. Start download.
2. Drop Wi-Fi for ~30 s, then restore.

**Expected results**

- Download resumes automatically without user action.
- 1.0 remains active until reboot.
- Device is working.

---

### TC-03: Long Wi-Fi drop (> 5 min) during download, optional update

**Priority: P1**

**Preconditions**

- Device on 1.0; optional 2.0 available

**Steps**

1. Start download.
2. Drop Wi-Fi for 6+ min, then restore.
3. Trigger manual retry.

**Expected results**

- Download does not resume automatically; user can retry manually.
- 1.0 remains active and device is working.
- Manual retry completes the download.

---

### TC-04: Long Wi-Fi drop (> 5 min) during download, mandatory update

**Priority: P1**

**Preconditions**

- Device on 1.0; mandatory 2.0 available

**Steps**

1. Start download.
2. Drop Wi-Fi for 6+ min, then restore.

**Expected results**

- Download retries automatically after Wi-Fi returns and completes.
- 1.0 active until reboot.
- Device is working.

---

### TC-05: Repeated Wi-Fi drops during download

**Priority: P2**

**Preconditions**

- Device on 1.0; 2.0 available

**Steps**

1. Start download.
2. Drop and restore Wi-Fi 5 times at ~20 s intervals.

**Expected results**

- No stuck "updating" state.
- Download completes or stops cleanly per retry rules.
- 1.0 active; device is working.

---

### TC-06: Partial download fails integrity check

**Priority: P0**

**Preconditions**

- Device on 1.0; 2.0 available

**Steps**

1. Start download.
2. Drop Wi-Fi so the image is incomplete; force the device to attempt verification/install (if possible).

**Expected results**

- Incomplete/corrupt image is rejected and not installed.
- 1.0 active; device is working.

---

### TC-07: Wi-Fi drop during install to inactive slot

**Priority: P0**

**Preconditions**

- Device on 1.0 (slot A); 2.0 fully downloaded and verified

**Steps**

1. Start install to slot B.
2. Drop Wi-Fi during install.

**Expected results**

- Install completes or is abandoned cleanly.
- Device continues running 1.0 from slot A and is working.

---

### TC-08: Wi-Fi drop during reboot into 2.0

**Priority: P0**

**Preconditions**

- 2.0 installed to slot B, reboot pending

**Steps**

1. Reboot.
2. Drop Wi-Fi during boot / first check-in.

**Expected results**

- Device boots into 2.0 and is working, or rolls back to 1.0 and is working.
- Never unbootable.

---

### TC-09: Wi-Fi drop while device is in screensaver

**Priority: P3**

**Preconditions**

- Device on 1.0, screensaver active, download in progress

**Steps**

1. Drop Wi-Fi for ~30 s, then restore.
2. Exit screensaver.

**Expected results**

- Download resumes automatically.
- 1.0 active; device is working.

---

### TC-10: Wi-Fi drop while device is in deep sleep

**Priority: P2**

**Preconditions**

- Device on 1.0; download started, device enters deep sleep

**Steps**

1. Drop Wi-Fi while asleep.
2. Restore Wi-Fi.
3. Wake device.

**Expected results**

- Device reconnects on wake; download resumes or retries per rules.
- 1.0 active; device is working.

---

### TC-11: TV off (USB power cut) during download

**Priority: P2**

**Preconditions**

- SETUP-01 confirms TV-off cuts power; device on 1.0, download in progress

**Steps**

1. Turn TV off mid-download.
2. Turn TV back on.

**Expected results**

- Device boots 1.0 and is working.
- Download resumes or retries per rules.

---

### TC-12: TV off (USB power cut) during install to inactive slot

**Priority: P0**

**Preconditions**

- SETUP-01 confirms TV-off cuts power; 2.0 installing to slot B

**Steps**

1. Turn TV off mid-install.
2. Turn TV back on.

**Expected results**

- Device boots 1.0 from slot A and is working.

---

### TC-13: TV off (USB power cut) during reboot into 2.0

**Priority: P0**

**Preconditions**

- SETUP-01 confirms TV-off cuts power; reboot into 2.0 in progress

**Steps**

1. Turn TV off during boot.
2. Turn TV back on.

**Expected results**

- Device boots 2.0 or rolls back to 1.0, and is working.
- Never unbootable.

---

### TC-14: Control: Wi-Fi drop during download on wall power

**Priority: P2**

**Preconditions**

- Device on 1.0, powered by wall adapter

**Steps**

1. Repeat TC-01 steps.

**Expected results**

- Same result as TC-01 (1.0 active, device working).

---

### TC-15: Wi-Fi drop during download while streaming

**Priority: P2**

**Preconditions**

- Device on 1.0, playing content; download in progress

**Steps**

1. Drop Wi-Fi for ~30 s, then restore.
2. Resume playback.

**Expected results**

- Playback can resume.
- Download resumes automatically.
- 1.0 active; no crash.

---

### TC-16: Wi-Fi drop during download while in a menu

**Priority: P3**

**Preconditions**

- Device on 1.0, in Settings menu; download in progress

**Steps**

1. Drop Wi-Fi for ~30 s, then restore.
2. Navigate menus.

**Expected results**

- Menu stays responsive.
- Download resumes automatically.
- 1.0 active; device is working.

---

### TC-17: Wi-Fi drop during download with low storage

**Priority: P2**

**Preconditions**

- Device on 1.0; free storage just above image size

**Steps**

1. Start download.
2. Drop Wi-Fi partway, then restore.

**Expected results**

- Partial file does not exhaust storage; download resumes or fails cleanly with a message.
- 1.0 active; device is working.

---

### TC-18: User presses remote buttons during Wi-Fi drop

**Priority: P3**

**Preconditions**

- Device on 1.0; download in progress

**Steps**

1. Drop Wi-Fi.
2. Press Home, Back, navigation and Play/Pause repeatedly for 60 s.
3. Restore Wi-Fi.

**Expected results**

- UI stays responsive, no crash or freeze.
- Download resumes.
- 1.0 active.

---

### TC-19: User starts playback right after Wi-Fi returns

**Priority: P3**

**Preconditions**

- Device on 1.0; download interrupted by Wi-Fi drop

**Steps**

1. Restore Wi-Fi.
2. Immediately start content playback.

**Expected results**

- Playback starts normally.
- Download resumes in background.
- 1.0 active until reboot.

# FW Update AI Pilot: Requirements (Wi-Fi interruption)

Requirements for firmware-update behavior when Wi-Fi or power is interrupted. Test cases are in [fw-update-test-cases.md](fw-update-test-cases.md).

**Status key**
- **Agreed**: confirmed by the team.
- **Proposed**: recommended, waiting for confirmation.

---

## 1. Device and environment

| ID | Requirement | Status |
|---|---|---|
| REQ-01 | The device is a Fire TV Stick with A/B partitions (slot A and slot B). | Agreed |
| REQ-02 | The device is powered from the TV's USB port. A wall adapter is used as the control setup. | Agreed |
| REQ-03 | In testing, a Wi-Fi drop is simulated at the router/AP, by turning the AP off or blocking the device. | Agreed |

## 2. Update flow

| ID | Requirement | Status |
|---|---|---|
| REQ-10 | The update downloads in the background. The current firmware stays active and the device keeps working during the download. | Agreed |
| REQ-11 | The downloaded image is integrity-checked (hash/signature). An incomplete or corrupt image is rejected and never installed. | Agreed |
| REQ-12 | The update is installed to the inactive slot and applied on reboot. Until the reboot, the current firmware stays active. | Agreed |
| REQ-13 | An interruption at any stage (download, install, reboot) must never leave the device unbootable. The device ends up on either the new or the previous firmware, and it is working. | Agreed |
| REQ-14 | Once the image is fully downloaded and verified, installing it needs no network connection. A Wi-Fi drop during install has no effect on the install. | Agreed |

## 3. Wi-Fi interruption during download

| ID | Requirement | Status |
|---|---|---|
| REQ-20 | The 5-minute timer starts when the download fails, which is the moment Wi-Fi drops. | Agreed |
| REQ-21 | While the timer is running, the device retries the download automatically every 60 s. | Agreed |
| REQ-22 | **Brief drop (Wi-Fi returns within 5 min):** the download resumes automatically, without user action. | Agreed |
| REQ-23 | **Long drop (more than 5 min), optional update:** automatic retries stop at 5 min. The user must start a retry manually. | Agreed |
| REQ-24 | **Long drop (more than 5 min), mandatory update:** timed retries stop at 5 min. The download then restarts automatically once Wi-Fi reconnects. The device never retries in an endless loop. | Agreed |
| REQ-25 | A download continues from where it stopped (resume). It restarts from 0% only when resuming is not possible, for example if the partial file is damaged or the server's image has changed. | Agreed |

## 4. State after retries stop

| ID | Requirement | Status |
|---|---|---|
| REQ-30 | After retries stop, the device never stays in a "downloading/updating" state. | Agreed |
| REQ-31 | **Optional update:** the end state is `DOWNLOAD_FAILED`. The partial download is kept so a retry can resume. The user sees this message with a **Retry** button: "Update couldn't be downloaded. Check your connection and try again." | Agreed |
| REQ-32 | **Mandatory update:** the end state is `WAITING_FOR_NETWORK`. The partial download is kept. No message is shown; the download restarts by itself when Wi-Fi returns (REQ-24). | Agreed |
| REQ-33 | In both cases, the current firmware stays active and the device is working. | Agreed |

## 5. Rollback

| ID | Requirement | Status |
|---|---|---|
| REQ-40 | A boot counts as failed if the new firmware does not reach the home screen. | Agreed |
| REQ-41 | After 3 failed boots in a row of the new firmware, the device switches back to the previous slot and boots the previous firmware. | Agreed |
| REQ-42 | After a rollback, the device is working on the previous firmware. | Agreed |

## 6. Settings preservation

| ID | Requirement | Status |
|---|---|---|
| REQ-50 | All user settings are kept after a successful update. | Agreed |
| REQ-51 | All user settings are also kept after a rollback to the previous firmware. | Agreed |

## 7. Additional update behaviors

Behaviors the sections above did not cover, first proposed as defaults for the simulator and then confirmed.

| ID | Requirement | Status |
|---|---|---|
| REQ-60 | During the 5-minute retry window, the download resumes as soon as Wi-Fi returns, without waiting for the next 60 s retry. | Agreed |
| REQ-61 | If the device reboots or loses power during a download, the kept partial download resumes automatically after boot, under the normal Wi-Fi rules. A device already in `DOWNLOAD_FAILED` or `WAITING_FOR_NETWORK` stays in that state. | Agreed |
| REQ-62 | Every new Wi-Fi drop starts a new 5-minute retry window. | Agreed |
| REQ-63 | A manual retry while Wi-Fi is still down fails once; the device stays in `DOWNLOAD_FAILED` with the message shown. | Agreed |
| REQ-64 | A rejected image is deleted. The device does not download it again by itself; a new download must be started. | Agreed |
| REQ-65 | Installation does not start automatically after a successful download; it is started separately. | Agreed |

## 8. Device behavior during an update

How the device must behave for the user while an update is in progress. These cover TC-09, TC-10 and TC-15 to TC-19.

| ID | Requirement | Status |
|---|---|---|
| REQ-70 | **Screensaver:** an active screensaver has no effect on the download. Wi-Fi drops are handled by the normal rules (REQ-20 to REQ-25), and exiting the screensaver does not interrupt the download. | Proposed |
| REQ-71 | **Deep sleep:** when the device wakes, it reconnects to Wi-Fi and an interrupted download resumes under the normal rules (REQ-20 to REQ-25). | Proposed |
| REQ-72 | **Menus and remote:** menus and remote input stay responsive during a download and during a Wi-Fi drop. The device does not crash or freeze. | Proposed |
| REQ-73 | **Low storage:** the download never uses more storage than the image size. If there is not enough free storage, the download stops cleanly with a message to the user, and the current firmware is unaffected. | Proposed |
| REQ-74 | **Playback:** content playback works normally during a download and right after Wi-Fi returns. The download continues in the background and does not block playback. | Proposed |

## 9. Definitions

| Term | Meaning |
|---|---|
| **Device is working** | Boots to the home screen, connects to Wi-Fi, plays content, and the remote responds. |
| **Version check** | Settings > About, plus ADB where available. |
| **Optional update** | The user decides when to retry after a long Wi-Fi drop. |
| **Mandatory update** | The device restarts the download by itself when Wi-Fi returns. |

## 10. Resolved questions

| ID | Question | Decision |
|---|---|---|
| OPEN-01 | Rollback trigger | 3 failed boots in a row (REQ-40, REQ-41) |
| OPEN-02 | Settings preservation | All settings, kept on update and on rollback (REQ-50, REQ-51) |
| OPEN-03 | Install without Wi-Fi | Install needs no network (REQ-14) |
| OPEN-04 | Message wording | Proposed text accepted (REQ-31) |

## 11. Changes from the earlier baseline

The baseline assumptions in [fw-update-test-cases.md](fw-update-test-cases.md) say "Retry policy: 10 retries x 60 s; the 5-minute cutoff takes precedence." Because the 5-minute cutoff always comes first, the 10-retry limit can never be reached. These requirements replace it with REQ-21: retry every 60 s, for at most 5 minutes. The test-case file has been updated to match.

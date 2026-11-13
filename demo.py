"""Run a few update scenarios and print what the simulated device does.

Usage:  python3 demo.py
"""
from fwsim import BootFailure, FirmwareImage, PowerLoss, Simulator, WifiDrop


def show(title: str, sim: Simulator) -> None:
    print(f"\n=== {title} ===")
    for e in sim.events:
        details = ", ".join(f"{k}={v}" for k, v in e.data.items() if k != "checksum")
        print(f"  t={e.t:>4}s  {e.name:<36} {details}")
    print(f"  -> state={sim.state}, running firmware {sim.active_version}, "
          f"settings={sim.settings}, working={sim.is_working}")
    if sim.message:
        print(f"  -> message shown: {sim.message!r}")


def full_update(sim: Simulator) -> Simulator:
    sim.start_download()
    sim.run()
    if sim.state == "DOWNLOADED":
        sim.install()
        sim.run()
        if sim.state == "REBOOT_PENDING":  # skip if the install was interrupted
            sim.reboot()
    return sim


settings = {"language": "en", "wifi": "home"}

# 1. Everything goes well.
show("Normal update", full_update(Simulator(settings=settings)))

# 2. Wi-Fi drops for 30 s at 40%: download resumes by itself (REQ-22, REQ-60).
show("Brief Wi-Fi drop (30 s)",
     full_update(Simulator(settings=settings, faults=[WifiDrop(at_percent=40, duration_s=30)])))

# 3. Wi-Fi drops for 6 min, optional update: retries stop, user must retry (REQ-23, REQ-31).
sim = Simulator(settings=settings, faults=[WifiDrop(at_percent=40, duration_s=360)])
sim.start_download()
sim.run()
show("Long Wi-Fi drop (6 min), optional update", sim)

# 4. Same drop, mandatory update: restarts by itself when Wi-Fi returns (REQ-24, REQ-32).
sim = Simulator(settings=settings, offered=FirmwareImage("2.0", mandatory=True),
                faults=[WifiDrop(at_percent=40, duration_s=360)])
sim.start_download()
sim.run()
show("Long Wi-Fi drop (6 min), mandatory update", sim)

# 5. TV turned off halfway through install: device stays on 1.0 (REQ-13).
show("Power loss during install",
     full_update(Simulator(settings=settings, faults=[PowerLoss(stage="install", at_percent=50)])))

# 6. New firmware fails to boot 3 times: rollback, settings kept (REQ-41, REQ-51).
show("New firmware fails to boot -> rollback",
     full_update(Simulator(settings=settings, faults=[BootFailure(times=3)])))

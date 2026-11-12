"""Firmware image offered by the (simulated) update server."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class FirmwareImage:
    version: str
    size_mb: int = 100
    mandatory: bool = False

    @property
    def checksum(self) -> str:
        """Expected hash of the complete image (REQ-11)."""
        return hashlib.sha256(f"{self.version}:{self.size_mb}".encode()).hexdigest()

"""Detect the Log profile of a Canon clip from its Custom Picture sidecar (.CPF). Read-only, stdlib only.

The profile name is stored in the .CPF as (index, value) byte pairs with incrementing index. Noise in code
values depends on the Log curve, so quietframe keeps separate calibration anchors per profile.
"""
from __future__ import annotations

from pathlib import Path

# Canon names as written in the sidecar -> quietframe profile keys.
KNOWN = (("Canon Log 3", "canon-log3"), ("Canon Log 2", "canon-log2"), ("Canon Log", "canon-log"))


def decode_cpf_names(data: bytes) -> list[str]:
    """Printable names stored as consecutive (index, value) pairs with incrementing index."""
    names: list[str] = []
    for start in range(0, len(data) - 4):
        index = data[start]
        if index == 0 or not (0x20 <= data[start + 1] < 0x7F):
            continue
        chars: list[str] = []
        position = start
        while position + 1 < len(data) and data[position] == (index + len(chars)) % 256:
            value = data[position + 1]
            if value == 0:
                break
            if not 0x20 <= value < 0x7F:
                chars = []
                break
            chars.append(chr(value))
            position += 2
        text = "".join(chars).strip()
        if len(text) >= 3 and text not in names:
            names.append(text)
    return names


def profile_from_cpf(cpf: Path) -> str | None:
    """quietframe profile key ('canon-log2', 'canon-log3', ...) or None when the sidecar says nothing known."""
    if not cpf.is_file():
        return None
    for name in decode_cpf_names(cpf.read_bytes()):
        for canon, key in KNOWN:
            if name.startswith(canon):
                return key
    return None


def find_sidecar(video: Path) -> Path | None:
    for suffix in (".CPF", ".cpf"):
        candidate = video.with_suffix(suffix)
        if candidate.is_file():
            return candidate
    return None


def detect(video: str) -> str | None:
    """Profile of a clip from the .CPF next to it; None if there is no sidecar (never guessed)."""
    sidecar = find_sidecar(Path(video))
    return profile_from_cpf(sidecar) if sidecar else None


def from_canon_name(name: str | None) -> str | None:
    """Map a name such as 'Canon Log 2' (e.g. from a plan file) to a profile key."""
    for canon, key in KNOWN:
        if name and name.startswith(canon):
            return key
    return None

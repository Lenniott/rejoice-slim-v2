"""Audio recording and device detection functionality."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Mapping, Sequence, cast

try:  # sounddevice is a required dependency, but be defensive for import-time errors
    import sounddevice as _sounddevice
except Exception:  # pragma: no cover - exercised only if dependency is missing
    _sounddevice = None

sd: Any = _sounddevice

logger = logging.getLogger(__name__)


def get_audio_input_devices() -> List[Dict[str, Any]]:
    """Return a list of available audio input devices.

    Each device is represented as a dict with at least:
    - ``index``: the device index as reported by sounddevice
    - ``name``: human-readable device name
    - ``is_default``: whether this is the default input device

    This function filters out devices that do not support audio input
    (``max_input_channels`` <= 0).

    Raises
    ------
    RuntimeError
        If the ``sounddevice`` dependency is not available.
    """

    if sd is None:  # pragma: no cover - requires missing dependency
        raise RuntimeError(
            "sounddevice library is not available. "
            "Please ensure it is installed and accessible."
        )

    # Query all devices from sounddevice. This returns a sequence of mapping-like
    # objects; we only rely on dict-style access for the keys we care about.
    raw_devices = list(cast(Sequence[Mapping[str, Any]], sd.query_devices()))

    # Determine default input device index, if any.
    default_index = None
    try:
        # sounddevice.default.device is typically a pair (input, output)
        default = getattr(sd, "default", None)
        if default and isinstance(default.device, (list, tuple)):
            default_index = default.device[0]
    except Exception:  # pragma: no cover - defensive only
        logger.debug("Unable to determine default audio input device", exc_info=True)

    input_devices: List[Dict[str, Any]] = []
    for index, dev in enumerate(raw_devices):
        # ``dev`` can be a dict-like object; use .get with a safe default.
        max_inputs = dev.get("max_input_channels", 0)
        if max_inputs and max_inputs > 0:
            name = dev.get("name", f"Device {index}")
            input_devices.append(
                {
                    "index": dev.get(
                        "index", index
                    ),  # some backends include explicit index
                    "name": name,
                    "is_default": (
                        default_index is not None
                        and dev.get("index", index) == default_index
                    ),
                    "raw": dev,
                }
            )

    return input_devices

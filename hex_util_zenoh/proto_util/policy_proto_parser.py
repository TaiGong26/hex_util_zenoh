################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-11-18
################################################################
"""Parser of the policy frames: transport fields only.

The parser carries a frame as bytes and checks its transport fields; nothing
here interprets what a field means. Frame shapes live in
``policy_proto_schema``, the meaning of a frame in ``proto_helper``, and the
endpoints in ``policy_middleware``.
"""

from __future__ import annotations

from typing import Mapping

import msgpack

from .policy_proto_schema import HeaderStamp


NS_PER_SEC = 1_000_000_000


def frame_keys(frame_type: type) -> frozenset:
    """Return the keys a frame type declares as required or optional.

    Args:
        frame_type (type): TypedDict of the protocol.

    Returns:
        frozenset: Declared keys, taken from the type itself.
    """
    required = getattr(frame_type, "__required_keys__", frozenset())
    optional = getattr(frame_type, "__optional_keys__", frozenset())
    return frozenset(required) | frozenset(optional)


def check_frame(
        frame: dict,
        frame_type: type) -> None:
    """Check that a frame carries every key its type declares.

    Args:
        frame (dict): Decoded frame.
        frame_type (type): TypedDict the frame has to satisfy.

    Raises:
        ValueError: If a declared key is missing.
    """
    declared = frame_keys(frame_type=frame_type)
    missing = [key for key in declared if key not in frame]
    if missing:
        raise ValueError(f"missing fields {sorted(missing)}")


def stamp_to_ns(stamp: Mapping[str, int]) -> int:
    """Convert a frame stamp to nanoseconds.

    Args:
        stamp (Mapping): Mapping with ``secs`` and ``nsecs``.

    Returns:
        int: Stamp in nanoseconds.

    Raises:
        ValueError: If the mapping is not a stamp.
    """
    if not isinstance(stamp, Mapping) or set(stamp) != {"secs", "nsecs"}:
        raise ValueError(
            f"stamp must be secs/nsecs, got {stamp!r}")
    return int(stamp["secs"]) * NS_PER_SEC + int(stamp["nsecs"])


def ns_to_stamp(stamp_ns: int) -> HeaderStamp:
    """Convert nanoseconds to a frame stamp.

    Args:
        stamp_ns (int): Time in nanoseconds.

    Returns:
        HeaderStamp: Mapping with ``secs`` and ``nsecs``.
    """
    value = int(stamp_ns)
    return {"secs": value // NS_PER_SEC, "nsecs": value % NS_PER_SEC}


def pack(frame: dict) -> bytes:
    """Serialise one frame.

    Args:
        frame (dict): Frame of the protocol.

    Returns:
        bytes: msgpack payload.

    Raises:
        ValueError: If the frame holds a value msgpack cannot express, for
            example an array.
    """
    try:
        return msgpack.packb(frame, use_bin_type=True)
    except (TypeError, ValueError) as error:
        raise ValueError(f"msgpack encode failed: {error}") from error


def unpack(payload: bytes) -> dict:
    """Deserialise one frame.

    Args:
        payload (bytes): msgpack payload.

    Returns:
        dict: Decoded frame.

    Raises:
        ValueError: If the payload is not a msgpack mapping.
    """
    try:
        frame = msgpack.unpackb(payload, raw=False)
    except Exception as error:
        raise ValueError(f"msgpack decode failed: {error}") from error
    if not isinstance(frame, dict):
        kind = type(frame).__name__
        raise ValueError(f"frame is {kind}, expected a mapping")
    return frame

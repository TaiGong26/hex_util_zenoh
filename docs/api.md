<h1 align="center">API</h1>

---

# Overview

This document lists all classes and functions provided by `hex_util_runtime`, organised by module.

All public symbols are importable directly from the top-level package:

```python
from hex_util_runtime import (
    # time_utils
    HexRate,
    ns_now, hex_ts_now, ns_to_hex_ts, hex_ts_to_ns, hex_ts_delta_ms,
    # buffer_utils
    HexShmRingBuffer, deque_helper,
    # env_util
    get_env_str, get_env_int, get_env_bool, get_env_float, get_env_ndarray,
    # file_utils
    hex_rmtree,
)
```

---

# `time_utils` — Time Management Utilities

## `ns_now() -> int`

Return the current time in nanoseconds.

- If the `HEX_PTP_CLOCK` environment variable is set to a PTP device path (e.g. `/dev/ptp0`), the returned value is the PTP hardware clock time via Linux `clock_gettime()` with a dynamic clock ID derived from the file descriptor.
- Otherwise, falls back to `time.perf_counter_ns()`.

```python
from hex_util_runtime import ns_now

t = ns_now()
print(f"now: {t} ns")  # e.g. "now: 1712345678901234567 ns"
```

## `hex_ts_to_ns(ts: dict) -> int`

Convert a hex timestamp dictionary to total nanoseconds.

| Parameter | Type | Description |
|-----------|------|-------------|
| `ts` | `dict` | Dictionary with keys `"s"` (seconds, int) and `"ns"` (nanoseconds, int) |

Returns total nanoseconds as `int`. Returns `np.inf` on error (e.g. missing keys).

```python
from hex_util_runtime import hex_ts_to_ns

ts = {"s": 1712345678, "ns": 901234567}
ns = hex_ts_to_ns(ts)  # 1712345678901234567
```

## `ns_to_hex_ts(ns: int) -> dict`

Convert nanoseconds to a hex timestamp dictionary.

| Parameter | Type | Description |
|-----------|------|-------------|
| `ns` | `int` | Total nanoseconds |

Returns `{"s": int, "ns": int}`.

```python
from hex_util_runtime import ns_to_hex_ts

ts = ns_to_hex_ts(1712345678901234567)
# {"s": 1712345678, "ns": 901234567}
```

## `hex_ts_now() -> dict`

Return the current time as a hex timestamp dictionary. Equivalent to `ns_to_hex_ts(ns_now())`.

Returns `{"s": int, "ns": int}`.

```python
from hex_util_runtime import hex_ts_now

ts = hex_ts_now()
print(f"{ts['s']}.{ts['ns']:09d} s")
```

## `hex_ts_delta_ms(curr_ts: dict, hdr_ts: dict) -> float`

Compute the difference between two hex timestamps in milliseconds.

| Parameter | Type | Description |
|-----------|------|-------------|
| `curr_ts` | `dict` | Current timestamp `{"s": ..., "ns": ...}` |
| `hdr_ts` | `dict` | Reference timestamp `{"s": ..., "ns": ...}` |

Returns `(curr_ts - hdr_ts)` in milliseconds as `float`. Returns `np.inf` on error.

```python
from hex_util_runtime import hex_ts_delta_ms

start = hex_ts_now()
# ... some work ...
end = hex_ts_now()
elapsed_ms = hex_ts_delta_ms(end, start)
```

## `HexRate` — Loop Rate Controller

Controls the execution rate of a loop by sleeping between iterations. Uses a hybrid approach: coarse `time.sleep()` for the bulk of the wait, then a spin-wait (busy loop) for the remaining microseconds to achieve precise timing.

### Constructor

```python
HexRate(hz: float, spin_threshold_ns: int = 10_000)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hz` | — | Target frequency in Hz (must be > 0) |
| `spin_threshold_ns` | `10_000` | Remaining time below which spin-wait is used instead of `time.sleep()` (nanoseconds) |

### Methods

| Method | Description |
|--------|-------------|
| `reset()` | Reset the next target time to `now + period`. Useful after a pause. |
| `sleep()` | Block until the next period boundary. If behind schedule, advances multiple periods to catch up without sleeping. |

### Behaviour details

- The period is computed as `1_000_000_000 / hz` nanoseconds.
- If the loop falls behind (i.e. `sleep()` is called after the target time), it silently skips missed periods by advancing the target by the required number of periods.
- The spin-wait yields (`time.sleep(0)`) if the remaining spin time exceeds 50 µs.

```python
from hex_util_runtime import HexRate, ns_now

rate = HexRate(100)  # 100 Hz loop
while True:
    rate.sleep()
    t = ns_now()
    # ... perform work ...
```

---

# `buffer_utils` — Shared Memory Ring Buffer

## `HexShmRingBuffer` — Lock-Free SPSC Shared Memory Ring Buffer

A **single-producer, single-consumer (SPSC)** ring buffer backed by POSIX shared memory, designed for high-frequency streaming (2–5 kHz+). The design favours **latest-read semantics** — always return the newest frame and discard backlog.

The buffer is lock-free: there are no mutexes or semaphores on the hot path. Only a `multiprocessing.Event` (`work_event`) is used as a shutdown flag.

### Constructor

```python
HexShmRingBuffer(capacity: int, dtype)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `capacity` | `int` | Number of elements in the ring |
| `dtype` | anything accepted by `np.dtype()` | Data type of each element (e.g. `np.float64`, `np.dtype('>u4')`) |

Allocates two POSIX shared memory blocks:
1. **Data buffer**: `capacity × item_size` bytes
2. **Index buffer**: 16 bytes, mapped as `np.ndarray((2,), dtype=np.int64)` — `idx[0]` is the write pointer, `idx[1]` is the read pointer (optional, for FIFO mode).

### Lifecycle Methods

| Method | Description |
|--------|-------------|
| `close()` | Release both shared memory blocks. Clears `work_event` first to signal shutdown. Idempotent. |

### Write / Read Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `write(data)` | `write(data: np.ndarray) -> None` | Lock-free write. If the buffer is full, the oldest entry is overwritten (read pointer advances). Copies `data.tobytes()` into the correct ring offset. |
| `read(latest: bool = False)` | `read(latest=False) -> Optional[scalar]` | Dispatches to `read_latest()` or `read_next()`. |
| `read_latest()` | `() -> Optional[scalar]` | **Recommended.** Returns the newest written element. Tracks last returned index to avoid duplicates. Returns `None` if no new data. |
| `read_next()` | `() -> Optional[scalar]` | FIFO read. Reads from the read index and increments it. Returns `None` if empty. Not recommended for high-frequency use. |

### Properties

| Attribute | Type | Description |
|-----------|------|-------------|
| `capacity` | `int` | Number of slots in the ring |
| `dtype` | `np.dtype` | Element data type |
| `item_size` | `int` | Element byte size |
| `work_event` | `multiprocessing.Event` | Shutdown flag; cleared by `close()`, set on construction |

### Producer/Consumer Example

**Producer process:**
```python
import numpy as np
from hex_util_runtime import HexShmRingBuffer

buf = HexShmRingBuffer(capacity=100, dtype=np.float64)
# ... share buf.shm.name and buf.idx_shm.name via some IPC ...

while running:
    data = np.float64(measure_sensor())
    buf.write(data)
```

**Consumer process:**
```python
import numpy as np
from multiprocessing import shared_memory
from hex_util_runtime import HexShmRingBuffer

# Reconstruct from names received via IPC
shm = shared_memory.SharedMemory(name=data_shm_name)
idx_shm = shared_memory.SharedMemory(name=idx_shm_name)
buf = HexShmRingBuffer.__new__(HexShmRingBuffer)
buf.shm = shm
buf.idx_shm = idx_shm
buf.idx = np.ndarray((2,), dtype=np.int64, buffer=idx_shm.buf)
# ... set other attributes ...

latest = buf.read_latest()  # get newest sample
```

> **Note**: In practice the consumer does not need to re-call `__new__` — the buffer is typically accessed from another process that constructs its own instance given the shared memory handles.

---

## `deque_helper(dq: deque, latest: bool = True) -> Any`

A standalone utility to drain a Python `collections.deque`.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dq` | — | A `collections.deque` instance |
| `latest` | `True` | If `True`, drains the entire deque and returns the **last (most recent)** element. If `False`, pops and returns the **leftmost (oldest)** element (FIFO). |

Returns the extracted element, or `None` if the deque is empty.

```python
from collections import deque
from hex_util_runtime import deque_helper

dq = deque()
dq.append("msg1")
dq.append("msg2")

latest = deque_helper(dq, latest=True)   # "msg2" (drains all)
oldest = deque_helper(dq, latest=False)  # None (already empty)
```

---

# `env_util` — Environment Variable Utilities

Type-safe readers for environment variables. All functions print a warning to stdout on parse failure.

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_env_str(key, default="") -> str` | Read a string env var. Returns `default` if unset or `None`. |
| `get_env_int(key, default=0) -> int` | Parse env var as `int`. Returns `default` on `ValueError`. |
| `get_env_bool(key) -> bool` | Returns `True` if the string is in `{"true", "1", "yes", "y"}` (case-insensitive). Any other value (including unset) returns `False`. |
| `get_env_float(key, default=0.0) -> float` | Parse env var as `float`. Returns `default` on `ValueError`. |
| `get_env_ndarray(key, default=np.zeros(1)) -> np.ndarray` | Split by `,` and parse as `float` numpy array. Returns `default` on `ValueError`. |

```python
from hex_util_runtime import get_env_bool, get_env_float, get_env_ndarray

debug = get_env_bool("DEBUG")              # true/1/yes/y → True
rate = get_env_float("CONTROL_RATE", 100.0)  # fallback to 100.0
gains = get_env_ndarray("KP_GAINS")          # "1.0,2.0,3.0" → array([1., 2., 3.])
```

---

# `file_utils` — File System Utilities

## `hex_rmtree(path: str) -> None`

Recursively remove a directory tree. A pure-`os` alternative to `shutil.rmtree`.

Returns early (no-op) if `path` does not exist. Walks the tree bottom-up, removing all files and subdirectories, then removes the root directory.

```python
from hex_util_runtime import hex_rmtree

# Safely remove a directory tree
hex_rmtree("/tmp/my_temp_dir")
```

---

# Notes

- All time functions use the singleton `HexTimeManager` under the hood, initialised at module import time.
- PTP clock integration is enabled by setting the `HEX_PTP_CLOCK` environment variable to a PTP device path (e.g. `/dev/ptp0`). Requires Linux and appropriate permissions.
- `HexShmRingBuffer` uses POSIX shared memory (`/dev/shm/`) and is **Linux-only**.
- Error handling throughout the library uses `print()` to stdout rather than Python's `logging` module.

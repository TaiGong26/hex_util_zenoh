<h1 align="center">HEXFELLOW RUNTIME UTILITIES</h1>

<p align="center">
    <a href="https://github.com/hexfellow/hex_util_runtime/stargazers">
        <img src="https://img.shields.io/github/stars/hexfellow/hex_util_runtime?style=flat-square&logo=github" />
    </a>
    <a href="https://github.com/hexfellow/hex_util_runtime/forks">
        <img src="https://img.shields.io/github/forks/hexfellow/hex_util_runtime?style=flat-square&logo=github" />
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://github.com/hexfellow/hex_util_runtime/issues">
        <img src="https://img.shields.io/github/issues/hexfellow/hex_util_runtime?style=flat-square&logo=github" />
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/python-≥3.8-blue?style=flat-square&logo=python" />
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/platform-Linux-orange?style=flat-square" />
</p>

---

# 📖 Overview

## What is `hex_util_runtime`

`hex_util_runtime` is a lightweight Python utility library providing essential runtime primitives with minimal dependencies. It is part of the HEXFELLOW ecosystem and serves as the foundational layer for time management, inter-process communication, environment configuration, and file system operations.

| Module | Primary Purpose | Key Components |
|--------|----------------|----------------|
| **time_utils** | High-precision time, PTP clock, loop rate control | `ns_now()`, `HexRate`, `HexTimeManager` |
| **buffer_utils** | Thread-safe variable + lock-free SPSC shared-memory ring buffer | `HexThreadingVar`, `HexShmRingBuffer`, `deque_helper` |
| **env_util** | Type-safe environment variable readers | `get_env_int()`, `get_env_bool()`, `get_env_ndarray()` |
| **file_utils** | Safe recursive directory removal | `hex_rmtree()` |

## What problem it solves

- **Unified time interface**: Abstract away the difference between system monotonic clocks and PTP hardware clocks behind a simple `ns_now()` call.
- **Thread-safe variable exchange**: Wrap any Python value with `HexThreadingVar` to safely read/write across threads using a mutex lock.
- **High-frequency inter-process streaming**: Provide a lock-free, single-producer-single-consumer shared-memory ring buffer (`HexShmRingBuffer`) optimized for 2–5 kHz+ data rates, avoiding serialization and IPC overhead.
- **Safe environment configuration**: Read environment variables with proper type conversion and fallback defaults, without repetitive `try/except` boilerplate.
- **Portable file operations**: Pure-`os` implementation of recursive directory deletion, removing the `shutil` dependency.

## Target users

- Robotics engineers who need low-latency, lock-free shared-memory communication between processes.
- Developers building real-time control loops with precise timing requirements.
- Anyone working in the HEXFELLOW ecosystem (`hex_driver_mujoco`, `hex_util_robot`, etc.) who needs runtime primitives.

## Project structure

```
hex_util_runtime/
├── hex_util_runtime/
│   ├── __init__.py         # Public exports (__all__)
│   ├── time_utils.py       # ns_now(), HexRate, HexTimeManager, hex timestamp converters
│   ├── buffer_utils.py     # HexThreadingVar (thread-safe variable), HexShmRingBuffer (lock-free SPSC SHM ring buffer), deque_helper
│   ├── env_util.py         # get_env_str/get_env_int/get_env_bool/get_env_float/get_env_ndarray
│   └── file_utils.py       # hex_rmtree (safe recursive directory removal)
├── docs/
│   ├── api.md              # Full API reference
│   └── example.md          # Usage walkthroughs
└── pyproject.toml          # Project metadata & build configuration
```

---

# 📦 Installation

## Requirements

- **Python** ≥ 3.8
- **OS**: Linux (POSIX shared memory and PTP clock support are Linux-specific)
- **Dependencies**:
  - `numpy ≥ 2.2.6`

## Install from PyPI

```bash
pip install hex_util_runtime
```

## Install from Source

We use [**uv**](https://github.com/astral-sh/uv) to manage the Python environment. Please install it first.

1. Clone and install in editable mode:

```bash
git clone https://github.com/hexfellow/hex_util_runtime.git
cd hex_util_runtime
./venv.sh
```

2. Activate before using:

```bash
source .venv/bin/activate
```

---

# ⚡ Quick Start

```python
from hex_util_runtime import ns_now, HexRate, hex_ts_now
from hex_util_runtime import get_env_int, hex_rmtree
from hex_util_runtime import HexThreadingVar, HexShmRingBuffer, deque_helper

# Get current time in nanoseconds
print(ns_now())

# Rate-limited loop (100 Hz)
rate = HexRate(100)
for _ in range(10):
    rate.sleep()
    print(f"ts: {hex_ts_now()}")

# Read an integer from environment (default 0)
interval = get_env_int("MY_INTERVAL_MS", default=50)
```

---

# 📑 Documentation

- [**API Reference**](docs/api.md) — Detailed documentation of all classes and functions.
- [**Examples**](docs/example.md) — Usage walkthroughs for each module.

---

# 📄 License

Apache License 2.0. See [LICENSE](LICENSE).

---

# 👥 Authors & Maintainers

| Role | Name | Email |
|------|------|-------|
| **Author** | Dong Zhaorui | joray.dong@hexfellow.com |
| **Maintainer** | jecjune (Chen Zejun) | zejun.chen@hexfellow.com |
| **Maintainer** | Dong Zhaorui | joray.dong@hexfellow.com |

---

# 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hexfellow/hex_util_runtime&type=Date)](https://star-history.com/#hexfellow/hex_util_runtime&Date)

---

# 👥 Contributors

<a href="https://github.com/hexfellow/hex_util_runtime/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=hexfellow/hex_util_runtime" />
</a>

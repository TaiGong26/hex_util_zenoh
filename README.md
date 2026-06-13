<h1 align="center">HEXFELLOW ZENOH UTILITIES</h1>

<p align="center">
    <a href="https://github.com/hexfellow/hex_util_zenoh/stargazers">
        <img src="https://img.shields.io/github/stars/hexfellow/hex_util_zenoh?style=flat-square&logo=github" />
    </a>
    <a href="https://github.com/hexfellow/hex_util_zenoh/forks">
        <img src="https://img.shields.io/github/forks/hexfellow/hex_util_zenoh?style=flat-square&logo=github" />
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://github.com/hexfellow/hex_util_zenoh/issues">
        <img src="https://img.shields.io/github/issues/hexfellow/hex_util_zenoh?style=flat-square&logo=github" />
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/python-≥3.8-blue?style=flat-square&logo=python" />
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <img src="https://img.shields.io/badge/platform-Linux-orange?style=flat-square" />
</p>

---

# 📖 Overview

## What is `hex_util_zenoh`

`hex_util_zenoh` is a lightweight Python wrapper around [Eclipse Zenoh](https://zenoh.io/), providing a simple pub/sub communication node API. It is part of the HEXFELLOW ecosystem and offers an intuitive interface for Zenoh-based inter-process and inter-machine communication.

| Module | Primary Purpose | Key Components |
|--------|----------------|----------------|
| **hex_zenoh_node** | Simple pub/sub node wrapping Zenoh sessions | `HexZenohNode` |

## What problem it solves

- **Simplified Zenoh API**: Wraps the Eclipse Zenoh Python bindings behind a minimal, ROS-like node interface (`create_pub`, `create_sub`, `pub`).
- **Easy publisher/subscriber management**: Automatically tracks and reuses publishers per topic. Subscribers automatically unwrap `ZBytes` payloads into plain `bytes` for user callbacks.
- **Thread-aware**: Designed to be used safely across threads with clear start/close lifecycle.

## Target users

- Robotics engineers who need lightweight, decentralised pub/sub communication.
- Developers using Eclipse Zenoh who want a simpler, more Pythonic API.
- Anyone building distributed systems in the HEXFELLOW ecosystem.

## Project structure

```
hex_util_zenoh/
├── hex_util_zenoh/
│   ├── __init__.py            # Public exports (HexZenohNode)
│   └── hex_zenoh_node.py      # HexZenohNode class
├── examples/
│   ├── talker.py              # TalkerNode example (ROS 2 talker style)
│   └── listener.py            # ListenerNode example (ROS 2 listener style)
├── docs/
│   └── api.md                 # API reference
├── pyproject.toml              # Project metadata & build configuration
└── venv.sh                     # Virtual environment setup script
```

---

# 📦 Installation

## Requirements

- **Python** ≥ 3.8
- **OS**: Linux (Zenoh runs on all major platforms; tested on Linux)
- **Dependencies**:
  - `eclipse-zenoh ≥ 1.0.0`

## Install from PyPI

```bash
pip install hex_util_zenoh
```

## Install from Source

We use [**uv**](https://github.com/astral-sh/uv) to manage the Python environment. Please install it first.

1. Clone and install in editable mode:

```bash
git clone https://github.com/hexfellow/hex_util_zenoh.git
cd hex_util_zenoh
./venv.sh
```

2. Activate before using:

```bash
source .venv/bin/activate
```

---

# ⚡ Quick Start

```python
from hex_util_zenoh import HexZenohNode

node = HexZenohNode()
node.start()

# Create a publisher and subscriber
node.create_pub("chatter")

def on_message(data: bytes):
    print(f"Received: {data.decode()}")

node.create_sub("chatter", on_message)

# Publish a message
node.pub("chatter", b"Hello, Zenoh!")

# Clean up
node.close()
```

### Running the examples

Open two terminals. In the first:

```bash
python examples/talker.py
```

In the second:

```bash
python examples/listener.py
```

---

# 📑 Documentation

- [**API Reference**](docs/api.md) — Detailed documentation of the `HexZenohNode` class.

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

[![Star History Chart](https://api.star-history.com/svg?repos=hexfellow/hex_util_zenoh&type=Date)](https://star-history.com/#hexfellow/hex_util_zenoh&Date)

---

# 👥 Contributors

<a href="https://github.com/hexfellow/hex_util_zenoh/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=hexfellow/hex_util_zenoh" />
</a>

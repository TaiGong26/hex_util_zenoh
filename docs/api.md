<h1 align="center">API Reference</h1>

---

# Overview

This document lists all classes provided by `hex_util_zenoh`.

All public symbols are importable directly from the top-level package:

```python
from hex_util_zenoh import HexZenohNode
```

---

# `HexZenohNode` — Simple Zenoh Communication Node

A lightweight wrapper around an Eclipse Zenoh session, providing a simple pub/sub interface. Designed to feel familiar to users of ROS 2 nodes.

## Constructor

```python
HexZenohNode(config: Optional[zenoh.Config] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `zenoh.Config` | `zenoh.Config()` | Zenoh configuration. If `None`, uses a default configuration with default scouting and peer discovery. |

The Zenoh session is **not** opened in the constructor. Call `start()` to establish the session.

## Lifecycle Methods

### `start() -> None`

Open the underlying Zenoh session and set `is_working` to `True`. Idempotent — calling it on an already-started node is a no-op.

```python
from hex_util_zenoh import HexZenohNode

node = HexZenohNode()
node.start()
# ... use the node ...
node.close()
```

### `close() -> None`

Close the Zenoh session and release all publishers and subscribers. Idempotent — safe to call multiple times.

```python
node.close()
```

## Properties

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_working` | `bool` | `True` after `start()` has been called, `False` after `close()` or before `start()`. |
| `session` | `Optional[zenoh.Session]` | The underlying Zenoh session. `None` before `start()` or after `close()`. |

## Publisher Methods

### `create_pub(topic_name: str) -> None`

Declare a publisher for the given topic. If a publisher for this topic already exists, this is a no-op.

| Parameter | Type | Description |
|-----------|------|-------------|
| `topic_name` | `str` | The Zenoh key expression (topic) to publish to. Supports Zenoh key expression syntax (e.g. `"robot/sensor/*"`). |

```python
node.create_pub("robot/imu")
```

### `pub(topic_name: str, data: bytes) -> None`

Publish raw bytes to the given topic. If no publisher exists for this topic, one is created automatically.

| Parameter | Type | Description |
|-----------|------|-------------|
| `topic_name` | `str` | The Zenoh key expression (topic) to publish to. |
| `data` | `bytes` | The payload to publish. |

```python
node.pub("chatter", b"Hello, World!")
```

## Subscriber Method

### `create_sub(topic_name: str, callback: Callable[[bytes], None]) -> None`

Declare a subscriber for the given topic. The callback receives the message payload as raw `bytes` (the Zenoh `ZBytes` payload is automatically unwrapped).

| Parameter | Type | Description |
|-----------|------|-------------|
| `topic_name` | `str` | The Zenoh key expression (topic) to subscribe to. |
| `callback` | `Callable[[bytes], None]` | Function called with the raw bytes payload of each received message. |

```python
def handle_message(data: bytes) -> None:
    print(f"Received: {data.decode()}")

node.create_sub("chatter", handle_message)
```

## Utility Methods

### `deque_helper(dq: deque, latest: bool = False) -> Optional[Any]` *(static)*

A helper for safely retrieving messages from a `collections.deque`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dq` | `deque` | — | The deque to pop from. |
| `latest` | `bool` | `False` | If `False`, pops and returns the oldest item (FIFO). If `True`, drains the entire deque and returns only the latest item. |

Returns the popped item, or `None` if the deque is empty.

```python
from collections import deque

self._queue = deque()
self._queue.append(b"msg1")
self._queue.append(b"msg2")

# Get oldest message
oldest = HexZenohNode.deque_helper(self._queue)  # b"msg1"

# Get latest message only
latest = HexZenohNode.deque_helper(self._queue, latest=True)  # b"msg2"
```

---

# Examples

## Talker

```python
import time
from hex_util_zenoh import HexZenohNode


class TalkerNode(HexZenohNode):
    """Publishes incrementing messages to 'chatter' every second."""

    def __init__(self):
        super().__init__()

    def start(self) -> None:
        super().start()
        self.create_pub("chatter")

    def pub_chatter(self, message: bytes) -> None:
        self.pub("chatter", message)


def main():
    node = TalkerNode()
    node.start()
    count = 0
    print("TalkerNode: Started publishing on 'chatter'...")
    try:
        while node.is_working:
            message = f"Hello World: {count}"
            node.pub_chatter(message.encode("utf-8"))
            print(f"TalkerNode: Published: '{message}'")
            count += 1
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        print("TalkerNode: Stopped.")


if __name__ == "__main__":
    main()
```

## Listener

```python
import time
from collections import deque
from hex_util_zenoh import HexZenohNode


class ListenerNode(HexZenohNode):
    """Subscribes to 'chatter' and queues received messages."""

    def __init__(self):
        super().__init__()
        self.__message_queue = deque()

    def on_message(self, data: bytes) -> None:
        self.__message_queue.append(data)

    def get_message(self, latest: bool = False) -> bytes:
        return self.deque_helper(self.__message_queue, latest)

    def start(self) -> None:
        super().start()
        self.create_sub("chatter", self.on_message)


def main():
    node = ListenerNode()
    node.start()
    print("ListenerNode: Listening on 'chatter'...")
    try:
        while node.is_working:
            message = node.get_message(latest=True)
            if message is not None:
                print(f"ListenerNode: Received: '{message.decode()}'")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        print("ListenerNode: Stopped.")


if __name__ == "__main__":
    main()
```

---

# Notes

- The Zenoh session must be started (`start()`) before creating publishers, subscribers, or publishing messages.
- `pub()` will automatically create a publisher if one does not exist for the given topic.
- Subscriber callbacks are invoked from Zenoh's internal I/O threads — keep callbacks fast.
- Use `deque_helper` to safely drain message queues in a thread-safe manner, picking either the oldest or latest message.
- For cross-machine communication, configure the Zenoh session via the `config` parameter (e.g., set peer endpoints, scouting settings, etc.).

#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-06-13
################################################################

import time
from collections import deque
from hex_util_zenoh import HexZenohNode


class ListenerNode(HexZenohNode):

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

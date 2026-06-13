#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-06-13
################################################################

import time
from hex_util_zenoh import HexZenohNode


class ListenerNode(HexZenohNode):

    def __init__(self):
        super().__init__()

    def on_message(self, data: bytes) -> None:
        print(f"ListenerNode: Received: '{data.decode('utf-8')}'")

    def run(self) -> None:
        self.start()
        self.create_sub("chatter", self.on_message)
        print("ListenerNode: Listening on 'chatter'...")
        try:
            while self.is_working:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.close()
            print("ListenerNode: Stopped.")


def main():
    node = ListenerNode()
    node.run()


if __name__ == "__main__":
    main()

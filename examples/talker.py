#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-06-13
################################################################

import time
from hex_util_zenoh import HexZenohNode


class TalkerNode(HexZenohNode):

    def __init__(self):
        super().__init__()

    def run(self) -> None:
        self.start()
        self.create_pub("chatter")
        count = 0
        print("TalkerNode: Started publishing on 'chatter'...")
        try:
            while self.is_working:
                message = f"Hello World: {count}"
                self.pub("chatter", message.encode("utf-8"))
                print(f"TalkerNode: Published: '{message}'")
                count += 1
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.close()
            print("TalkerNode: Stopped.")


def main():
    node = TalkerNode()
    node.run()


if __name__ == "__main__":
    main()

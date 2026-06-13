#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-06-13
################################################################

import zenoh
from typing import Callable, Dict, Optional


class HexZenohNode:

    def __init__(self, config: Optional[zenoh.Config] = None):
        self._config = config if config is not None else zenoh.Config()
        self._session: Optional[zenoh.Session] = None
        self._publishers: Dict[str, zenoh.Publisher] = {}
        self._subscribers: Dict[str, zenoh.Subscriber] = {}
        self._is_working = False

    @property
    def session(self) -> Optional[zenoh.Session]:
        return self._session

    @property
    def is_working(self) -> bool:
        return self._is_working

    def start(self) -> None:
        if self._session is not None:
            return
        self._session = zenoh.open(self._config)
        self._is_working = True

    def close(self) -> None:
        if not self._is_working:
            return
        self._is_working = False

        if self._session is None:
            return
        self._publishers.clear()
        self._subscribers.clear()
        self._session.close()
        self._session = None

    def create_pub(self, topic_name: str) -> zenoh.Publisher:
        if self._session is None:
            raise RuntimeError("Session not opened. Call open() first.")
        if topic_name in self._publishers:
            return self._publishers[topic_name]
        publisher = self._session.declare_publisher(topic_name)
        self._publishers[topic_name] = publisher
        return publisher

    def create_sub(self, topic_name: str,
                   callback: Callable[[bytes], None]) -> zenoh.Subscriber:
        if self._session is None:
            raise RuntimeError("Session not opened. Call open() first.")

        def _zenoh_callback(sample: zenoh.Sample) -> None:
            payload = sample.payload.to_bytes()
            callback(payload)

        subscriber = self._session.declare_subscriber(topic_name,
                                                      _zenoh_callback)
        self._subscribers[topic_name] = subscriber
        return subscriber

    def pub(self, topic_name: str, data: bytes) -> None:
        if self._session is None:
            raise RuntimeError("Session not opened. Call open() first.")
        publisher = self._publishers.get(topic_name)
        if publisher is None:
            publisher = self.create_pub(topic_name)
        publisher.put(data)

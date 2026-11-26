################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-11-18
################################################################
"""Contract of the policy frames.

A frame is described once, as a ``TypedDict``; the key table, the missing key
check and the stamp conversion are derived from it, so adding a field never
means editing a second list. Nothing but ``typing`` is imported here, so the
file can move to a transport utility package as it stands.
"""

from __future__ import annotations

from typing import TypedDict


class HeaderStamp(TypedDict):
    """Stamp of a frame, seconds plus nanoseconds.

    Attributes:
        secs (int): Whole seconds.
        nsecs (int): Nanoseconds within the second.
    """
    secs: int
    nsecs: int


class ImagePayload(TypedDict):
    """One image inside an observation frame.

    Attributes:
        encoding (str): ``jpeg`` for colour, ``mono16`` for depth.
        width (int): Image width in pixels.
        height (int): Image height in pixels.
        data (bytes): Encoded or raw bytes.
    """

    encoding: str
    width: int
    height: int
    data: bytes


class CameraPayload(TypedDict):
    """One camera inside an observation frame.

    Attributes:
        rgb (ImagePayload): Colour frame.
        depth (ImagePayload | None): Depth frame when the camera has one.
    """

    rgb: ImagePayload
    depth: ImagePayload | None


class ArmPayload(TypedDict):
    """One arm and its gripper inside an observation frame.

    Attributes:
        pos (list): Joint positions.
        vel (list): Joint velocities.
        eff (list): Joint efforts.
        pose (list): End effector pose as position and quaternion.
        grip_pos (list): Gripper position.
        grip_vel (list): Gripper velocity.
        grip_eff (list): Gripper effort.
    """

    pos: list[float]
    vel: list[float]
    eff: list[float]
    pose: list[float]
    grip_pos: list[float]
    grip_vel: list[float]
    grip_eff: list[float]


class ObservationFrame(TypedDict):
    """Observation frame sent to the model side.

    The observation has a link of its own, so no field has to say what it is.

    Attributes:
        header (HeaderStamp): Frame stamp produced by the observation layer.
        camera (dict): Camera payloads keyed by the model field name.
        arm (dict): Arm payloads keyed by the model field name.
    """

    header: HeaderStamp
    camera: dict[str, CameraPayload]
    arm: dict[str, ArmPayload]


class InferenceFrame(TypedDict):
    """Inference enable flag sent to the model side on every tick.

    Attributes:
        inference_enabled (bool): Whether the robot is running and accepts
            actions.
    """

    inference_enabled: bool


class DualArmActionManipFrame(TypedDict):
    """Action chunk frame received from the model side.

    Attributes:
        header (HeaderStamp): Reference time of the chunk.
        chunk_step_interval_ms (int): Duration of one step.
        action_mode (str): Mode of the steps, carried as the sender wrote
            it; the action layer decides what it means.
        arm_ctrl_mode (str): One of ``ARM_CTRL_MODES``.
        arm (dict): Arm steps keyed by the model field name, each of shape
            ``(steps, dof)``.
        grip (dict): Gripper steps keyed by the model field name, each of shape
            ``(steps, dof)``.
    """

    header: HeaderStamp
    chunk_step_interval_ms: int
    action_mode: str
    arm_ctrl_mode: str
    arm: dict[str, list[list[float]]]
    grip: dict[str, list[list[float]]]

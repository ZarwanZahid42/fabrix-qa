"""
Module 1 — Video/Frame Ingestion
==================================
Responsible for:
  - Connecting to IP cameras or local webcams via RTSP / USB
  - Pulling frames at a configurable FPS
  - Forwarding raw frames to the preprocessing pipeline

TODO:
  - Implement RTSPStreamHandler class using OpenCV VideoCapture
  - Add frame buffering / queue to avoid backpressure
  - Emit frames over a local ZeroMQ or asyncio Queue to the AI inference module
"""

from __future__ import annotations


class StreamHandler:
    """Placeholder — to be implemented in Phase 2."""

    def __init__(self, source: str, fps: int = 25) -> None:
        self.source = source
        self.fps = fps

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

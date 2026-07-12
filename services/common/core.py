# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""Shared plumbing for TransEg services: config, mock switch, typed layers."""
import os

LAYERS = ("HumanIdentity", "Representation", "DigitalTwin", "TransEg")

def is_mock() -> bool:
    # Mock is the safe default: no model, no network, deterministic.
    return os.environ.get("TRANSEG_MOCK", "1") != "0"

def backend_url(name: str, default: str) -> str:
    return os.environ.get(f"TRANSEG_{name.upper()}_URL", default)

def assert_layer(layer: str) -> str:
    """The four layers are typed and never conflated (CONTRACT §2)."""
    if layer not in LAYERS:
        raise ValueError(f"unknown identity layer {layer!r}; must be one of {LAYERS}")
    return layer

"""Year 10 extension: translate the browser's algorithms into Python.

Run the tests on the Pi with:
    python3 -m unittest discover -s chromebook-app -p 'test_python_bridge.py'

This file does not connect to the house or use GPIO.
"""


def command_for(device, action):
    """Return the MQTT payload, or None for an unknown device/action."""
    # TODO: translate the corrected JavaScript commandFor() mapping.
    return None


def count_active(states):
    """Count True values; ignore False and None (unknown)."""
    # TODO: use a loop and a counter. Explain why None is not active.
    return 0

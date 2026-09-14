#!/usr/bin/env python3
"""
Simpson's House: servo calibration tool.

Find the open and closed position for each door, save them, and the house
uses them. You do not need to edit mqttlistener.py.

How to run it (on the Raspberry Pi):
    cd ~/simpsons-house
    sudo systemctl stop simpsons-house.service
    mqttenv/bin/python servo_calibrate.py

Commands:
    g         choose the GARAGE door
    d         choose the FRONT door
    45        move the door to 45 degrees (any number from 0 to 180)
    +  or  -  nudge the door 5 degrees  (+10 or -2 also work)
    closed    save where the door is now as its CLOSED position
    open      save where the door is now as its OPEN position
    test      swing the door closed, open, closed using the saved positions
    show      list the saved positions for both doors
    reset     put the chosen door back to open 90, closed 0
    q         quit

Angles are saved to servo_angles.json in the same folder as this file.
"""

import json
import os
import time

import RPi.GPIO as GPIO

GARAGE_SERVO_PIN = 27   # Garage door servo  (physical pin 13)
SERVO_PIN        = 23   # Front door servo   (physical pin 16)

# mqttlistener.py looks for this file in the same folder, so keep it here
ANGLES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "servo_angles.json")
DEFAULT_ANGLES = {
    "garage": {"open": 90, "closed": 0},
    "door":   {"open": 90, "closed": 0},
}
NAMES = {"garage": "Garage door", "door": "Front door"}
NUDGE = 5


def angle_to_duty(angle):
    """Same formula as mqttlistener.py: 0 degrees = 2% duty, 180 degrees = 12%."""
    return (angle / 180.0) * 10 + 2


def load_angles():
    """Read saved angles, using the defaults for anything missing or invalid."""
    angles = {door: dict(positions) for door, positions in DEFAULT_ANGLES.items()}
    try:
        with open(ANGLES_FILE) as f:
            saved = json.load(f)
        for door in angles:
            for position in ("open", "closed"):
                value = saved.get(door, {}).get(position)
                if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 180:
                    angles[door][position] = int(value)
    except FileNotFoundError:
        pass
    except (OSError, ValueError, AttributeError):
        print("  (servo_angles.json could not be read, so the defaults are being used)")
    return angles


def save_angles(angles):
    """Write to a temporary file first, so a crash never leaves a half-written file."""
    tmp = ANGLES_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(angles, f, indent=2)
        f.write("\n")
    os.replace(tmp, ANGLES_FILE)


def show(angles):
    for door in ("garage", "door"):
        print(f"  {NAMES[door]:<12} closed = {angles[door]['closed']:>3}°    open = {angles[door]['open']:>3}°")


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(GARAGE_SERVO_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(SERVO_PIN, GPIO.OUT, initial=GPIO.LOW)
pwms = {
    "garage": GPIO.PWM(GARAGE_SERVO_PIN, 50),
    "door":   GPIO.PWM(SERVO_PIN, 50),
}
for pwm in pwms.values():
    pwm.start(0)


def move(door, angle):
    """Send the door to one angle, then stop pulsing so the servo does not hum."""
    pwms[door].ChangeDutyCycle(angle_to_duty(angle))
    time.sleep(0.6)
    pwms[door].ChangeDutyCycle(0)
    print(f"  {NAMES[door]} moved to {angle}°")


angles = load_angles()
current = "garage"
position = {"garage": None, "door": None}   # last angle we moved each door to

print(__doc__)
print("Saved positions right now:")
show(angles)
print(f"\nYou are adjusting the {NAMES[current].upper()}. Type d to switch.\n")

try:
    while True:
        raw = input(f"[{NAMES[current]}] > ").strip().lower()
        if not raw:
            continue

        if raw == "q":
            break

        elif raw in ("g", "d"):
            current = "garage" if raw == "g" else "door"
            print(f"  Now adjusting the {NAMES[current].upper()}  "
                  f"(saved: closed {angles[current]['closed']}°, open {angles[current]['open']}°)")

        elif raw in ("open", "closed"):
            if position[current] is None:
                print("  Move the door first by typing an angle, then save it.")
                continue
            angles[current][raw] = position[current]
            try:
                save_angles(angles)
            except OSError as e:
                print(f"  Could not save: {e}")
                print("  If it says permission denied, run:  sudo chown pi:pi servo_angles.json")
                continue
            print(f"  Saved: {NAMES[current]} {raw.upper()} = {position[current]}°")

        elif raw == "test":
            closed, opened = angles[current]["closed"], angles[current]["open"]
            print(f"  Testing {NAMES[current]}: closed {closed}°, open {opened}°, closed {closed}°")
            for angle in (closed, opened, closed):
                move(current, angle)
                time.sleep(0.8)
            position[current] = closed

        elif raw == "show":
            show(angles)

        elif raw == "reset":
            angles[current] = dict(DEFAULT_ANGLES[current])
            try:
                save_angles(angles)
            except OSError as e:
                print(f"  Could not save: {e}")
                continue
            print(f"  {NAMES[current]} reset to closed 0°, open 90°")

        elif raw[0] in "+-":
            if position[current] is None:
                print("  Type an angle first, then nudge from there.")
                continue
            try:
                step = int(raw[1:]) if raw[1:] else NUDGE
            except ValueError:
                print("  Use + or - on their own, or with a number like +10")
                continue
            target = position[current] + step if raw[0] == "+" else position[current] - step
            new = max(0, min(180, target))
            move(current, new)
            position[current] = new
            if new != target:
                print(f"  (stopped at {new}°, the {'highest' if new == 180 else 'lowest'} angle a servo can go)")

        else:
            try:
                angle = int(round(float(raw)))
            except ValueError:
                print("  Not a command I know. Type a number, or one of: g d + - closed open test show reset q")
                continue
            if not 0 <= angle <= 180:
                print("  The angle must be between 0 and 180.")
                continue
            move(current, angle)
            position[current] = angle

finally:
    for pwm in pwms.values():
        pwm.stop()
    GPIO.cleanup()
    print("\nFinished. Start the house again with:")
    print("  sudo systemctl start simpsons-house.service")

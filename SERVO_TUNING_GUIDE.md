# Servo Tuning Guide

Set how far the front door and garage door open and close.

You will use a small program called `servo_calibrate.py`. **You do not need to
edit any code.** You move each door until it looks right, type `open` or
`closed`, and the house remembers it.

Every house is cut and glued slightly differently, so every house needs its own
positions. It takes about five minutes.

---

## What you need

- The Raspberry Pi switched on, with both servos wired (see `WIRING_GUIDE.md`)
- Your house in front of you, so you can watch the doors move
- A terminal connected to the Pi (Secure ShellFish on the iPad, or SSH)

---

## Step 1: Get the latest version

Go to the project folder and download any updates:

```bash
cd ~/simpsons-house
git pull
```

If `git pull` prints an error about local changes, see
[Troubleshooting](#troubleshooting) at the bottom of this guide.

---

## Step 2: Stop the house program

The house program runs in the background all the time, and it is in control of
the servos. Stop it so the calibration tool can use them instead:

```bash
sudo systemctl stop simpsons-house.service
```

---

## Step 3: Start the calibration tool

```bash
mqttenv/bin/python servo_calibrate.py
```

Type it exactly like that. Plain `python3` will not work, because the servo
library is installed inside the project's `mqttenv` folder.

The tool prints its list of commands and the positions saved right now. The
prompt tells you which door you are adjusting:

```
[Garage door] >
```

It always starts on the **garage door**.

Every command is explained, with examples, in the
[Command reference](#command-reference) further down.

---

## Step 4: Set the CLOSED position

1. Type `0` and press Enter. Watch the door move.
2. If the door is not fully shut, try other numbers such as `10` or `20`.
   You can also type `+` or `-` to nudge the door 5 degrees at a time.
3. When the door looks properly shut, type `closed` and press Enter.

You will see a message like this:

```
Saved: Garage door CLOSED = 10°
```

---

## Step 5: Set the OPEN position

1. Type `90` and press Enter.
2. Adjust with numbers, `+` or `-` until the door looks properly open.
3. Type `open` and press Enter.

```
Saved: Garage door OPEN = 75°
```

---

## Step 6: Check it

Type `test` and press Enter.

The door closes, opens, then closes again, using the positions you saved. If
either end is not quite right, go back to Step 4 or Step 5 and save it again.
Saving again simply replaces the old number.

---

## Step 7: Do the front door

Type `d` and press Enter to switch to the front door.

Repeat **Steps 4, 5 and 6** for the front door. (Type `g` to switch back to the
garage door at any time.)

---

## Step 8: Finish

Type `q` and press Enter to quit. Then start the house program again:

```bash
sudo systemctl start simpsons-house.service
```

Open the app on the iPad and try both doors. They now use your saved positions.

**Do not skip this step.** Until you start the house program again, the iPad
buttons will not do anything.

---

## How to read the examples

The examples below are copied from the real tool. Each one looks like this:

```
[Garage door] > 45
  Garage door moved to 45°
```

- `[Garage door] >` is the **prompt**. The tool is waiting for you, and the
  word in the brackets tells you which door you are adjusting.
- `45` is **what you type**. Type it, then press **Enter**.
- The indented line underneath is **what the tool replies**.

Commands are not case sensitive, so `OPEN`, `Open` and `open` all work. Type
one command per line.

---

## Command reference

### `g` and `d`: choose a door

**Syntax**

```
g
d
```

`g` chooses the garage door, `d` chooses the front door. The tool starts on the
garage door.

**Example**

```
[Garage door] > d
  Now adjusting the FRONT DOOR  (saved: closed 0°, open 90°)
[Front door] > g
  Now adjusting the GARAGE DOOR  (saved: closed 0°, open 90°)
```

**Good to know**
- When you switch, the tool shows that door's saved positions.
- Check the word in the prompt before saving, so you save the right door.

---

### A number: move the door to an angle

**Syntax**

```
ANGLE
```

`ANGLE` is a whole number from `0` to `180`.

**Examples**

```
[Garage door] > 0
  Garage door moved to 0°
[Garage door] > 45
  Garage door moved to 45°
[Garage door] > 180
  Garage door moved to 180°
```

**Good to know**
- Moving the door does **not** save anything. Use `closed` or `open` to save.
- A decimal is rounded to the nearest whole number: `45.6` moves to `46°`.
- A number above 180 is refused:

  ```
  [Garage door] > 200
    The angle must be between 0 and 180.
  ```

- A number that starts with `+` or `-` is a **nudge**, not an angle. See the
  next command.

---

### `+` and `-`: nudge the door

**Syntax**

```
+
-
+AMOUNT
-AMOUNT
```

`+` on its own adds 5 degrees. `-` on its own takes away 5 degrees. Add a number
straight after the sign, with no space, to nudge by that amount instead.

**Examples**

```
[Garage door] > 60
  Garage door moved to 60°
[Garage door] > +
  Garage door moved to 65°
[Garage door] > -
  Garage door moved to 60°
[Garage door] > +10
  Garage door moved to 70°
[Garage door] > -2
  Garage door moved to 68°
```

**Good to know**
- You must move the door to an angle first, so the tool knows where to nudge from:

  ```
  [Garage door] > +
    Type an angle first, then nudge from there.
  ```

- `+` makes the number bigger. Which way the door physically moves depends on
  how your servo is mounted.
- The door cannot go past 0 or 180. The tool tells you when it stops:

  ```
  [Garage door] > 178
    Garage door moved to 178°
  [Garage door] > +
    Garage door moved to 180°
    (stopped at 180°, the highest angle a servo can go)
  ```

- Leave no space between the sign and the number. `+ 10` does not work; `+10` does.
- `-1` means "nudge down 1 degree", not "move to minus 1".

---

### `closed`: save the closed position

**Syntax**

```
closed
```

Saves the angle you **last moved the door to** as this door's closed position.

**Example**

```
[Garage door] > 10
  Garage door moved to 10°
[Garage door] > closed
  Saved: Garage door CLOSED = 10°
```

**Good to know**
- You must move the door first:

  ```
  [Garage door] > closed
    Move the door first by typing an angle, then save it.
  ```

- It saves the angle the tool sent, not a position you pushed the door to by hand.
- Saving again replaces the old number. There is no need to delete anything first.
- The house uses the new number straight away.

---

### `open`: save the open position

**Syntax**

```
open
```

Works exactly like `closed`, but saves the open position.

**Example**

```
[Garage door] > 75
  Garage door moved to 75°
[Garage door] > open
  Saved: Garage door OPEN = 75°
```

---

### `test`: try the saved positions

**Syntax**

```
test
```

Moves the chosen door to its saved closed position, then open, then closed again.

**Example**

```
[Garage door] > test
  Testing Garage door: closed 10°, open 75°, closed 10°
  Garage door moved to 10°
  Garage door moved to 75°
  Garage door moved to 10°
```

**Good to know**
- `test` uses the **saved** numbers, so it shows exactly what the iPad will do.
- If you have not saved anything yet, it uses closed 0° and open 90°.

---

### `show`: list the saved positions

**Syntax**

```
show
```

**Example**

```
[Front door] > show
  Garage door  closed =  10°    open =  75°
  Front door   closed =   0°    open =  85°
```

Shows both doors, whichever one you are adjusting.

---

### `reset`: go back to the starting positions

**Syntax**

```
reset
```

Puts the **chosen door only** back to closed 0°, open 90°. The other door is not
changed.

**Example**

```
[Front door] > reset
  Front door reset to closed 0°, open 90°
```

---

### `q`: quit

**Syntax**

```
q
```

**Example**

```
[Front door] > q

Finished. Start the house again with:
  sudo systemctl start simpsons-house.service
```

Your saved positions are kept after you quit. Remember to run the command it
shows you (Step 8).

---

### When the tool does not understand

If you type something it does not know, it tells you and nothing moves:

```
[Garage door] > abc
  Not a command I know. Type a number, or one of: g d + - closed open test show reset q
```

Check the spelling and try again.

---

## Worked examples

### Example 1: Setting up a new house

Both doors, from start to finish.

```
[Garage door] > 0
  Garage door moved to 0°
[Garage door] > +
  Garage door moved to 5°
[Garage door] > +
  Garage door moved to 10°
[Garage door] > closed
  Saved: Garage door CLOSED = 10°
[Garage door] > 90
  Garage door moved to 90°
[Garage door] > 75
  Garage door moved to 75°
[Garage door] > open
  Saved: Garage door OPEN = 75°
[Garage door] > test
  Testing Garage door: closed 10°, open 75°, closed 10°
  Garage door moved to 10°
  Garage door moved to 75°
  Garage door moved to 10°
[Garage door] > d
  Now adjusting the FRONT DOOR  (saved: closed 0°, open 90°)
[Front door] > 0
  Front door moved to 0°
[Front door] > closed
  Saved: Front door CLOSED = 0°
[Front door] > 90
  Front door moved to 90°
[Front door] > -5
  Front door moved to 85°
[Front door] > open
  Saved: Front door OPEN = 85°
[Front door] > test
  Testing Front door: closed 0°, open 85°, closed 0°
  Front door moved to 0°
  Front door moved to 85°
  Front door moved to 0°
[Front door] > show
  Garage door  closed =  10°    open =  75°
  Front door   closed =   0°    open =  85°
[Front door] > q
```

What happened:
1. The garage door was not quite shut at 0°, so it was nudged to 10° and saved as closed.
2. 90° opened it too far, so 75° was tried and saved as open.
3. `test` confirmed both, then `d` switched to the front door.
4. The front door was shut at 0°, and 5° less than 90° looked best for open.
5. `show` confirmed both doors before quitting.

---

### Example 2: The door opens the wrong way

The garage door swings shut when it should open. The servo is mounted the other
way round, which is fine. Save the numbers the other way round instead:

```
[Garage door] > 90
  Garage door moved to 90°
[Garage door] > closed
  Saved: Garage door CLOSED = 90°
[Garage door] > 0
  Garage door moved to 0°
[Garage door] > open
  Saved: Garage door OPEN = 0°
[Garage door] > test
  Testing Garage door: closed 90°, open 0°, closed 90°
  Garage door moved to 90°
  Garage door moved to 0°
  Garage door moved to 90°
```

Closed does not have to be the smaller number. No rewiring or remounting needed.

---

### Example 3: The servo buzzes at one end

At 180° the servo buzzes and feels warm. It is pushing against its internal stop.
Back off until the buzzing stops, then save that:

```
[Garage door] > 180
  Garage door moved to 180°
[Garage door] > 170
  Garage door moved to 170°
[Garage door] > 165
  Garage door moved to 165°
[Garage door] > open
  Saved: Garage door OPEN = 165°
[Garage door] > test
  Testing Garage door: closed 0°, open 165°, closed 0°
  Garage door moved to 0°
  Garage door moved to 165°
  Garage door moved to 0°
```

Most servos are happiest 10 to 15 degrees away from 0 and 180.

---

### Example 4: Fixing one position later

Both doors are already set up, but the front door does not open quite far enough.
Only the open position needs changing:

```
[Garage door] > show
  Garage door  closed =  10°    open =  75°
  Front door   closed =   5°    open =  85°
[Garage door] > d
  Now adjusting the FRONT DOOR  (saved: closed 5°, open 85°)
[Front door] > 90
  Front door moved to 90°
[Front door] > +5
  Front door moved to 95°
[Front door] > open
  Saved: Front door OPEN = 95°
[Front door] > test
  Testing Front door: closed 5°, open 95°, closed 5°
  Front door moved to 5°
  Front door moved to 95°
  Front door moved to 5°
```

The closed position (5°) and the whole garage door were left alone.

---

### Example 5: Starting again

The front door settings have got muddled. Reset just that door and set it up again:

```
[Garage door] > d
  Now adjusting the FRONT DOOR  (saved: closed 40°, open 150°)
[Front door] > reset
  Front door reset to closed 0°, open 90°
[Front door] > show
  Garage door  closed =  10°    open =  75°
  Front door   closed =   0°    open =  90°
```

The garage door kept its positions. Now carry on from Step 4 for the front door.

---

## Where are my positions saved?

In a file called `servo_angles.json` in the project folder. You can look at it:

```bash
cat ~/simpsons-house/servo_angles.json
```

The house program reads this file every time a door opens or closes. Each Pi
keeps its own file, so your positions will not change when you run `git pull`,
and they do not affect anyone else's house.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| `ModuleNotFoundError: No module named 'RPi'` | You typed `python3`. Use `mqttenv/bin/python servo_calibrate.py` |
| `No such file or directory` | You are not in the project folder. Type `cd ~/simpsons-house` first |
| Nothing moves when you type an angle | The house program is still running. Do Step 2 |
| `Not a command I know` when you type `open` | You have an old version of the tool. Quit with `q` and do Step 1 |
| `Move the door first` | Type an angle before typing `open` or `closed` |
| `Could not save: Permission denied` | Type `sudo chown pi:pi servo_angles.json`, then save again |
| `git pull` says *your local changes would be overwritten* | Someone edited the code by hand earlier. Type `git stash`, then `git pull` again. Then set your positions with this tool |
| The iPad buttons do nothing | You have not started the house program again. Do Step 8 |
| The iPad still uses the old positions | Check you saw a `Saved:` message. Run `cat servo_angles.json` to confirm the numbers |
| The door twitches slightly | Normal for these servos. Nothing to fix |
| The Pi restarts when a door moves | The servos are drawing too much power from the Pi. Ask your teacher about an external 5V supply |

---

## How it works

This section is for anyone curious about what is happening underneath. You do
not need it to tune your doors.

### How a servo hears an angle

A servo does not understand degrees. It listens for a pulse, repeated 50 times
a second, and moves to the position that pulse length stands for.

```
   one cycle = 20 ms  (50 times per second)
   |<--------------------------------->|
    ____                                ____
   |    |______________________________|    |____
   |<-->|
   pulse length decides the position

   0.4 ms  =    0 degrees
   1.4 ms  =   90 degrees
   2.4 ms  =  180 degrees
```

The house program turns an angle into a pulse with this line in
`set_servo_angle()`:

```python
duty = (angle / 180.0) * 10 + 2
```

Duty cycle is the percentage of each cycle that the pulse is switched on.

| Angle | Duty cycle | Pulse |
|---|---|---|
| 0° | 2% | 0.4 ms |
| 45° | 4.5% | 0.9 ms |
| 90° | 7% | 1.4 ms |
| 135° | 9.5% | 1.9 ms |
| 180° | 12% | 2.4 ms |

After each move, the program stops sending pulses. The servo then runs cool and
quiet, but it no longer holds the door firmly, so you can push a door by hand.
That is deliberate.

### How the saved positions reach the doors

`servo_calibrate.py` writes your positions to `servo_angles.json`:

```json
{
  "garage": {
    "open": 75,
    "closed": 10
  },
  "door": {
    "open": 85,
    "closed": 0
  }
}
```

When the iPad sends OPEN or CLOSE, `mqttlistener.py` reads that file and looks up
the right number:

```python
angles = load_servo_angles()["garage"]
angle  = angles["open"] if open_door else angles["closed"]
```

If the file is missing, or a number in it is not between 0 and 180, the program
uses 90° for open and 0° for closed instead.

---

## Advanced: making the doors move slowly

This is the one change that does need code, so treat it as an extension task.

The servo always moves at full speed. An SG90 covers about 60 degrees in a tenth
of a second, so the door snaps open. To make it swing, the program has to step
through the angles in between.

Add this function to `mqttlistener.py`, just below `set_servo_angle()`:

```python
def sweep_servo_angle(pwm, start, end, label="Servo", seconds=1.5, steps=50):
    """Move gradually from start to end so the door swings instead of snapping."""
    try:
        for i in range(steps + 1):
            angle = start + (end - start) * (i / steps)
            pwm.ChangeDutyCycle((angle / 180.0) * 10 + 2)
            time.sleep(seconds / steps)
        pwm.ChangeDutyCycle(0)
        logger.info(f"{label} swept {start}° to {end}° over {seconds}s")
        return True
    except Exception as e:
        logger.error(f"Servo sweep failed ({label}): {e}")
        return False
```

Then, in `control_garage_door()`, replace the `set_servo_angle(...)` line with:

```python
if open_door:
    start, end = angles["closed"], angles["open"]
else:
    start, end = angles["open"], angles["closed"]
success = sweep_servo_angle(GARAGE_SERVO_PWM, start, end,
                            label="Garage Door Servo", seconds=2.0)
```

It still uses the positions you saved with the calibration tool.

- A bigger `seconds` number makes the door slower
- A bigger `steps` number makes it smoother. Below about 20 it looks jerky

Restart the house program after changing the code:

```bash
sudo systemctl restart simpsons-house.service
```

A slow sweep keeps the motor working for longer, so it is more likely to make
the Pi restart if both doors move at once.

---

## See also

- `WIRING_GUIDE.md`: wiring the servos
- `EXTENSION_GUIDE.md`: adding your own devices to the house
- `TEACHING_GUIDE.md`: how a tap on the iPad becomes movement on the Pi

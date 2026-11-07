# Extension Guide: Adding Your Own Devices

For students who have the light, garage door and front door working, and want
to add a device of their own.

You will add **one new device from start to finish**:

1. wire it to the Raspberry Pi
2. teach the Pi's program (`mqttlistener.py`) how to control it
3. add a button for it in the control interface

The example in this guide is a **doorbell buzzer** on GPIO 5. Once it works, you
can use exactly the same steps for an LED, a fan, or anything else that is
simply on or off.

Unlike servo tuning, this extension **does** involve editing code. Writing that
code is the point of the extension. Every step tells you which file to open,
what to search for, and exactly what to type.

---

## Contents

- [Safety first](#safety-first)
- [Before you start](#before-you-start)
- [How to read the steps](#how-to-read-the-steps)
- [Part 1: Wire the buzzer](#part-1-wire-the-buzzer) (Step 1)
- [Part 2: The Raspberry Pi](#part-2-the-raspberry-pi) (Steps 2 to 13)
- [Part 3: The iPad app](#part-3-the-ipad-app) (Steps 14 to 21)
- [Tool reference](#tool-reference): nano, py_compile, systemctl, journalctl, mosquitto_pub, mosquitto_sub
- [Checklist](#checklist)
- [Troubleshooting](#troubleshooting)
- [Motors: DC and stepper](#motors-dc-and-stepper)
- [Harder extensions](#harder-extensions)

---

## Safety first

- **Low voltage only.** Everything in this project runs on 3.3V or 5V from the
  Pi. Never connect anything to mains power.
- **Switch the Pi off** before adding or moving any wire.
- **Check the current.** A GPIO pin can safely supply about 16 mA, and all the
  pins together about 50 mA. An LED or a small buzzer is fine. A motor is not.
  See [Motors](#motors-dc-and-stepper).
- If anything gets hot or smells, unplug the Pi straight away.

---

## Before you start

**1. Your house works.** The light and both doors work from the device.

**2. You have the latest version.** On the Pi:

```bash
cd ~/simpsons-house
git pull
```

If `git pull` shows an error, see *Getting the latest version* in the README.

**3. You have a backup.** Copy the Pi's program before you change it:

```bash
cp mqttlistener.py mqttlistener.backup.py
```

If your changes go badly wrong, you can put the original back at any time:

```bash
cp mqttlistener.backup.py mqttlistener.py
sudo systemctl restart simpsons-house.service
```

**4. You can use `nano`.** It is the text editor you will use on the Pi. The
[Tool reference](#nano-edit-a-file-on-the-pi) explains the keys you need.

**5. The controller is open on the device**. You will need it in
Part 3.

---

## How to read the steps

Each code step looks like this:

**File:** the file to open.

**Search for:** a short piece of text to find with nano's search (`Ctrl+W`).
It takes you straight to the right place.

**Before:** what the code looks like now.

**After:** what it should look like when you have finished. The new lines are
the ones that were not in *Before*.

Three rules that prevent most mistakes:

- **Copy spacing exactly.** Python uses the spaces at the start of a line to
  work out which code belongs together. Use spaces, not Tab, and line your new
  code up with the lines around it.
- **Spelling and capitals matter.** `BUZZER_PIN`, `buzzer_pin` and `Buzzer_Pin`
  are three different names to Python.
- **Do one step at a time.** Save, check, then move on.

Our device uses these names throughout. If you build a different device, pick
your own names and use them every time.

| Thing | Name used in this guide |
|---|---|
| GPIO pin | `5` (physical pin 29) |
| Pin name in Python | `BUZZER_PIN` |
| MQTT topic | `home/buzzer` |
| Topic name in Python | `TOPIC_BUZZER` |
| State name | `buzzer` in Python, `buzzerOn` in Swift |
| Control function | `control_buzzer()` in Python, `toggleBuzzer()` in Swift |

---

## Part 1: Wire the buzzer

### Step 1: Wire it

**Switch the Pi off first.**

There are two kinds of buzzer. This guide needs an **active** buzzer, which beeps
as soon as it gets power. A **passive** buzzer stays silent unless it is sent a
PWM signal. If yours is passive, it will not beep with these steps. Ask your
teacher for an active one, or try the [PWM extension](#a-device-with-a-range-not-just-on-and-off).

The longer leg is `+`.

```
Pi GPIO 5  (physical pin 29) ─── Buzzer (+) long leg
Pi GND     (physical pin 30) ─── Buzzer (−) short leg
```

**Choosing a different pin.** Pins already used by the house: **17** (light),
**23** (front door servo), **27** (garage servo). Free pins you can use:
**5, 6, 12, 13, 16, 19, 20, 21, 26**. Run `pinout` on the Pi to see where each
one is on the board.

Switch the Pi back on.

---

## Part 2: The Raspberry Pi

### Step 2: Open the Pi's program

```bash
cd ~/simpsons-house
nano mqttlistener.py
```

Keep it open for Steps 3 to 10. Save as you go with `Ctrl+O` then `Enter`.

---

### Step 3: Add the pin

**File:** `mqttlistener.py`  **Search for:** `Front Door Servo signal`

**Before:**

```python
SERVO_PIN        = 23   # Front Door Servo signal wire
```

**After:**

```python
SERVO_PIN        = 23   # Front Door Servo signal wire
BUZZER_PIN       = 5    # Doorbell buzzer (+) leg
```

This gives the pin number a name, so the rest of the program can say
`BUZZER_PIN` instead of remembering `5`.

---

### Step 4: Add the topic

**File:** `mqttlistener.py`  **Search for:** `"home/door"`

**Before:**

```python
TOPIC_DOOR   = "home/door"     # iPad sends "ON" or "OFF" here
```

**After:**

```python
TOPIC_DOOR   = "home/door"     # iPad sends "ON" or "OFF" here
TOPIC_BUZZER = "home/buzzer"   # iPad sends "ON" or "OFF" here
```

A topic is like a channel name. The iPad sends messages to `home/buzzer`, and
the Pi listens on it. **Both sides must spell it exactly the same.**

---

### Step 5: Add the buzzer to the state tracker

**File:** `mqttlistener.py`  **Search for:** `device_states = {`

**Before:**

```python
device_states = {
    "light":  False,
    "garage": False,
    "door":   False
}
```

**After:**

```python
device_states = {
    "light":  False,
    "garage": False,
    "door":   False,
    "buzzer": False
}
```

> **Watch the comma.** You must add a comma to the end of the `"door"` line.
> Every item except the last one needs a comma after it. This is the most common
> mistake in the whole extension.

> **The name must match the topic.** The program works out this name from the
> last part of the topic, so `home/buzzer` becomes `"buzzer"`. If they do not
> match, the buzzer works but the Pi cannot report its state.

---

### Step 6: Set up the pin

**File:** `mqttlistener.py`  **Search for:** `GPIO.setup(SERVO_PIN`

**Before:**

```python
    GPIO.setup(SERVO_PIN, GPIO.OUT, initial=GPIO.LOW)
```

**After:**

```python
    GPIO.setup(SERVO_PIN, GPIO.OUT, initial=GPIO.LOW)

    # Set up the buzzer pin as an output, starting LOW (silent)
    GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW)
```

Note the **4 spaces** at the start of each new line, matching the line above.

`GPIO.OUT` means the Pi sends power out of this pin. `initial=GPIO.LOW` means it
starts switched off, so the buzzer does not scream when the house starts up.

---

### Step 7: Listen on the new topic

**File:** `mqttlistener.py`  **Search for:** `for topic in`

**Before:**

```python
        for topic in [TOPIC_LIGHT, TOPIC_GARAGE, TOPIC_DOOR]:
```

**After:**

```python
        for topic in [TOPIC_LIGHT, TOPIC_GARAGE, TOPIC_DOOR, TOPIC_BUZZER]:
```

Change the existing line. Do not add a new one.

> **This is the step people forget.** Without it, everything else looks right,
> but the Pi never hears a single buzzer message.

---

### Step 8: Write the control function

**File:** `mqttlistener.py`  **Search for:** `Door control error`

This takes you to the end of `control_door()`.

**Before:**

```python
    except Exception as e:
        logger.error(f"❌ Door control error: {e}")
        return False
```

**After:**

```python
    except Exception as e:
        logger.error(f"❌ Door control error: {e}")
        return False


def control_buzzer(state: bool) -> bool:
    """
    Turn the doorbell buzzer on or off.

    TEACHING: An active buzzer beeps whenever its pin is HIGH,
    so this works exactly like control_light().
    """
    try:
        GPIO.output(BUZZER_PIN, GPIO.HIGH if state else GPIO.LOW)
        logger.info(f"🔔 Doorbell Buzzer → {'ON' if state else 'OFF'}")
        return True
    except Exception as e:
        logger.error(f"❌ Buzzer control error: {e}")
        return False
```

- Leave **two blank lines** above `def control_buzzer`.
- `def` starts at the very beginning of the line, with no spaces.
- The emoji are optional. You can leave them out.

`GPIO.HIGH if state else GPIO.LOW` means: if `state` is `True`, switch the pin
on, otherwise switch it off. The function returns `True` if it worked, so the
rest of the program knows whether to report success.

---

### Step 9: Send buzzer messages to your function

**File:** `mqttlistener.py`  **Search for:** `unknown topic`

This takes you to the end of the list of topics inside `on_message()`.

**Before:**

```python
            success = control_door(command_state)

        else:
            logger.warning(f"⚠️  Message on unknown topic: {topic}")
```

**After:**

```python
            success = control_door(command_state)

        elif topic == TOPIC_BUZZER:
            valid_commands = {"ON": True, "OFF": False}
            device_name    = "Doorbell Buzzer"
            command_state  = valid_commands.get(payload)
            if command_state is None:
                publish_error(topic, f"Invalid command: {payload}. Use ON or OFF.")
                return
            success = control_buzzer(command_state)

        else:
            logger.warning(f"⚠️  Message on unknown topic: {topic}")
```

Your new `elif` goes **above** the `else:`, lined up with it (8 spaces).

What it does, line by line:
- `elif topic == TOPIC_BUZZER:` runs this block only for buzzer messages.
- `valid_commands` lists the words the buzzer accepts and what they mean.
- `valid_commands.get(payload)` turns `"ON"` into `True`, `"OFF"` into `False`, and
  anything else into `None`.
- If it is `None`, the Pi reports an error and stops.
- Otherwise it calls your `control_buzzer()` from Step 8.

---

### Step 10: Switch the buzzer off when the house stops

**File:** `mqttlistener.py`  **Search for:** `Light off`

**Before:**

```python
        GPIO.output(LIGHT_PIN, GPIO.LOW)  # Light off
```

**After:**

```python
        GPIO.output(LIGHT_PIN, GPIO.LOW)  # Light off
        GPIO.output(BUZZER_PIN, GPIO.LOW) # Buzzer off
```

This runs when the house program shuts down, so the buzzer never gets stuck on.

**Save and close nano:** `Ctrl+O`, `Enter`, then `Ctrl+X`.

---

### Step 11: Check for typing mistakes

Before restarting the house, ask Python to check the file:

```bash
mqttenv/bin/python -m py_compile mqttlistener.py
```

**If there are no mistakes, it prints nothing** and you go straight back to the
prompt. That is what you want.

If there is a mistake, it tells you the line number. For example, a missing
comma from Step 5:

```
  File "mqttlistener.py", line 77
    "door":   False
              ^^^^^
SyntaxError: invalid syntax. Perhaps you forgot a comma?
```

Open the file again at that line with `nano +77 mqttlistener.py`, fix it, save,
and run the check again. Repeat until it prints nothing.

`py_compile` only finds typing mistakes. A misspelled name, like `BUZZER_PN`,
is only found when the program runs, in Step 12.

---

### Step 12: Restart the house and read the log

```bash
sudo systemctl restart simpsons-house.service
sudo journalctl -u simpsons-house.service -n 20 --no-pager
```

The first command starts the house again with your new code. The second shows
the last 20 lines of its log.

Each log line starts with the date and time. **Look for this line:**

```
[INFO] Simpson's House: 📡 Subscribed to: home/buzzer
```

- **You can see it:** Steps 3 to 10 are working. Go to Step 13.
- **You see `Fatal error: name 'BUZZER_PIN' is not defined`:** Step 3 is missing,
  or the name is spelled differently in two places.
- **The log stops without `Subscribed to: home/buzzer`:** check Step 7.

More messages are explained in [Troubleshooting](#troubleshooting).

---

### Step 13: Test the Pi on its own

Test the Pi **before** touching the app. If something is wrong now, you know it
is in the Python code, not the Swift code.

**Turn the buzzer on:**

```bash
mosquitto_pub -h localhost -t home/buzzer -m ON
```

The buzzer should beep. The command itself prints nothing.

**Turn it off:**

```bash
mosquitto_pub -h localhost -t home/buzzer -m OFF
```

**Check what the Pi reported back:**

```bash
mosquitto_sub -h localhost -v -t home/buzzer/status -C 1
```

```
home/buzzer/status OFF
```

It prints the buzzer's last reported state and returns to the prompt. Turn the
buzzer on again and repeat the check to see `ON`.

**Read the log again:**

```bash
sudo journalctl -u simpsons-house.service -n 6 --no-pager
```

```
[INFO] Simpson's House: 📨 Command received: home/buzzer → ON
[INFO] Simpson's House: 🔔 Doorbell Buzzer → ON
[INFO] Simpson's House: ✅ Doorbell Buzzer command executed successfully
[INFO] Simpson's House: 📨 Command received: home/buzzer → OFF
[INFO] Simpson's House: 🔔 Doorbell Buzzer → OFF
[INFO] Simpson's House: ✅ Doorbell Buzzer command executed successfully
```

**If the buzzer beeps and the log looks like that, the whole Pi side is
finished.** Do not start Part 3 until it does.

---

## Part 3: The iPad app

The app is written in Swift. You will change three files. Open the Simpson's
House app in Swift Playgrounds: the files are listed in the sidebar on the left.
Tap a file name to open it.

To find text in a file, use **Find** (`⌘F` on a keyboard). The **Search for**
text in each step finds exactly one place.

### Step 14: Check the app still runs

Before changing anything, run the app once and make sure it connects to your
house. If it does not work now, it will not work after your changes either, and
you will not know why.

---

### Step 15: Add the buzzer's state

**File:** `Models.swift`  **Search for:** `var doorOpen`

This file says *DO NOT EDIT*. Adding a device is the one time you are meant to.

**Before:**

```swift
    @Published var doorOpen = false
```

**After:**

```swift
    @Published var doorOpen = false
    @Published var buzzerOn = false
```

`@Published` means the screen updates by itself whenever this value changes.

---

### Step 16: Add the toggle function

**File:** `MQTTClient.swift`  **Search for:** `func toggleDoor`

Scroll down to the closing `}` of `toggleDoor()`.

**Before:**

```swift
    func toggleDoor() {
        let newState = !deviceStates.doorOpen
        deviceStates.doorOpen = newState
        receivedMessages.append("DEBUG: Door toggled to \(newState ? "OPEN" : "CLOSED")")
        publishCommand(topic: "home/door", command: newState ? "ON" : "OFF", device: "Front Door")
    }
```

**After:**

```swift
    func toggleDoor() {
        let newState = !deviceStates.doorOpen
        deviceStates.doorOpen = newState
        receivedMessages.append("DEBUG: Door toggled to \(newState ? "OPEN" : "CLOSED")")
        publishCommand(topic: "home/door", command: newState ? "ON" : "OFF", device: "Front Door")
    }

    func toggleBuzzer() {
        let newState = !deviceStates.buzzerOn
        deviceStates.buzzerOn = newState
        receivedMessages.append("DEBUG: Buzzer toggled to \(newState ? "ON" : "OFF")")
        publishCommand(topic: "home/buzzer", command: newState ? "ON" : "OFF", device: "Doorbell Buzzer")
    }
```

What it does:
- `!deviceStates.buzzerOn` flips the state: on becomes off, off becomes on.
- `publishCommand` sends `ON` or `OFF` to `home/buzzer`. That is the same topic
  and the same words the Pi expects from Steps 4 and 9.

---

### Step 17: Undo the button if sending fails

**File:** `MQTTClient.swift`  **Search for:** `deviceStates.doorOpen.toggle()`

**Before:**

```swift
                    else if topic == "home/door" { self?.deviceStates.doorOpen.toggle() }
```

**After:**

```swift
                    else if topic == "home/door" { self?.deviceStates.doorOpen.toggle() }
                    else if topic == "home/buzzer" { self?.deviceStates.buzzerOn.toggle() }
```

If the message cannot be sent, this flips the button back so it does not show
`ON` when nothing happened.

---

### Step 18: Add the button

**File:** `DeviceControlsSection.swift`  **Search for:** `.gridCellColumns(2)`

**Before:**

```swift
                    action: { mqttClient.toggleDoor() }
                )
                .gridCellColumns(2)
```

**After:**

```swift
                    action: { mqttClient.toggleDoor() }
                )
                .gridCellColumns(2)

                // Doorbell Buzzer: tapping toggles the buzzer on GPIO 5
                DeviceCard(
                    icon: "bell.fill",
                    title: "Doorbell",
                    subtitle: "Buzzer",
                    isOn: mqttClient.deviceStates.buzzerOn,
                    accentColor: .red,
                    action: { mqttClient.toggleBuzzer() }
                )
```

What each part means:

| Part | Meaning | Try changing it to |
|---|---|---|
| `icon` | The picture, an SF Symbols name | `"bell.fill"`, `"fan.fill"`, `"speaker.wave.2.fill"`, `"lightbulb.fill"` |
| `title` | Large text on the card | any text in quotes |
| `subtitle` | Small text under the title | any text in quotes |
| `isOn` | Whether the card shows as on | the state from Step 15 |
| `accentColor` | The card's colour when on | `.red`, `.blue`, `.green`, `.orange` |
| `action` | What happens when the card is tapped | the function from Step 16 |

Add `.gridCellColumns(2)` on the line after the closing `)` if you want your card
to fill the whole row.

---

### Step 19: Fix the device counter

**File:** `DeviceControlsSection.swift`

The badge at the top says how many devices are on, out of 3. You now have 4.

**Search for:** `activeDevicesCount)/3`

**Before:**

```swift
                Text("\(activeDevicesCount)/3 Active")
```

**After:**

```swift
                Text("\(activeDevicesCount)/4 Active")
```

**Search for:** `doorOpen   { count`

**Before:**

```swift
        if mqttClient.deviceStates.doorOpen   { count += 1 }
```

**After:**

```swift
        if mqttClient.deviceStates.doorOpen   { count += 1 }
        if mqttClient.deviceStates.buzzerOn   { count += 1 }
```

---

### Step 20: Add the topic to the list (optional)

**File:** `MQTTClient.swift`  **Search for:** `GPIO 23 - Front Door Servo`

Near the top there is a list of topics. The app does not actually use this list.
It is there as a record, so keep it accurate for the next person who reads the code.

**Before:**

```swift
        "home/door"     // GPIO 23 - Front Door Servo
    ]
```

**After:**

```swift
        "home/door",    // GPIO 23 - Front Door Servo
        "home/buzzer"   // GPIO 5  - Doorbell Buzzer
    ]
```

Add a comma to the end of the `"home/door"` line.

---

### Step 21: Run it

Run the app and connect to your house.

1. A **Doorbell** card appears under the Front Door card.
2. Tap it. The buzzer beeps, and the card shows as on.
3. The number on the badge goes up by one, and now counts out of 4.
4. Tap it again. The buzzer stops.

If the app shows red error marks and will not run, see the Swift section of
[Troubleshooting](#troubleshooting).

> **Good to know.** The card shows what the app *sent*. The app does not listen
> for replies from the Pi. If the card is on but the buzzer is silent, test the
> Pi on its own again (Step 13). That tells you whether the problem is on the
> Pi or in the app.

**You have added a device.** To add another, go back to Step 1 and use new names.

---

## Tool reference

### `nano`: edit a file on the Pi

**Syntax**

```bash
nano FILENAME
nano +LINE FILENAME
```

**Examples**

```bash
nano mqttlistener.py          # open the file at the top
nano +77 mqttlistener.py      # open the file at line 77
```

**Keys** (`Ctrl+W` means hold `Ctrl` and press `W`)

| Keys | What it does |
|---|---|
| `Ctrl+W`, type text, `Enter` | Search for text |
| `Ctrl+W`, `Enter` | Search for the same text again |
| `Ctrl+O`, `Enter` | Save |
| `Ctrl+X` | Close. If it asks *Save modified buffer?*, press `Y` then `Enter` |
| `Ctrl+K` | Cut the whole line |
| `Ctrl+U` | Paste the line back |
| `Alt+U` | Undo |
| `Ctrl+C` | Show which line you are on |

---

### `py_compile`: check Python for typing mistakes

**Syntax**

```bash
mqttenv/bin/python -m py_compile FILENAME
```

**Example**

```bash
mqttenv/bin/python -m py_compile mqttlistener.py
```

**Output**

- **Nothing** means no typing mistakes were found.
- An error names the line number:

  ```
    File "mqttlistener.py", line 77
      "door":   False
                ^^^^^
  SyntaxError: invalid syntax. Perhaps you forgot a comma?
  ```

- Spacing problems give an `IndentationError`, for example:

  ```
  Sorry: IndentationError: unindent does not match any outer indentation level (mqttlistener.py, line 412)
  ```

---

### `systemctl`: start, stop and restart the house

**Syntax**

```bash
sudo systemctl ACTION simpsons-house.service
```

| `ACTION` | What it does |
|---|---|
| `restart` | Stop the house program and start it again. Use this after changing code |
| `stop` | Stop the house program |
| `start` | Start the house program |
| `status` | Show whether it is running |

**Example**

```bash
sudo systemctl status simpsons-house.service --no-pager
```

Look for `Active: active (running)`. If it says `failed`, read the log with
`journalctl` to find out why.

---

### `journalctl`: read the house program's log

**Syntax**

```bash
sudo journalctl -u simpsons-house.service OPTIONS
```

| Option | What it does |
|---|---|
| `-u simpsons-house.service` | Only show the house program's messages |
| `-n 20` | Show the last 20 lines. Change the number as you like |
| `--no-pager` | Print the lines and return to the prompt |
| `-f` | Keep watching and show new lines as they happen. Press `Ctrl+C` to stop |

**Examples**

```bash
sudo journalctl -u simpsons-house.service -n 20 --no-pager   # the last 20 lines
sudo journalctl -u simpsons-house.service -f                 # watch live
```

Watching live is useful in a second terminal window while you test from
another window or from the iPad.

---

### `mosquitto_pub`: send a message

Acts like the iPad app: sends one message to a topic.

**Syntax**

```bash
mosquitto_pub -h localhost -t TOPIC -m MESSAGE
```

| Part | Meaning |
|---|---|
| `-h localhost` | Send it to the broker on this Pi |
| `-t TOPIC` | The topic, for example `home/buzzer` |
| `-m MESSAGE` | The message, for example `ON` |

**Examples**

```bash
mosquitto_pub -h localhost -t home/buzzer -m ON
mosquitto_pub -h localhost -t home/buzzer -m OFF
mosquitto_pub -h localhost -t home/light -m ON
mosquitto_pub -h localhost -t home/garage -m OPEN
```

**Output:** none. Check the result with `mosquitto_sub` or `journalctl`.

**Good to know**
- The message is changed to capitals, so `on` works the same as `ON`.
- The topic is **not** changed. `home/Buzzer` and `home/buzer` are different
  topics, and the Pi ignores them without logging anything.

---

### `mosquitto_sub`: watch messages

Listens on a topic and prints each message that arrives.

**Syntax**

```bash
mosquitto_sub -h localhost -v -t TOPIC
```

| Part | Meaning |
|---|---|
| `-h localhost` | Listen to the broker on this Pi |
| `-v` | Print the topic name as well as the message |
| `-t TOPIC` | The topic to watch. `#` means "everything below here" |
| `-C 1` | Stop after one message and return to the prompt |

**Example 1: check the buzzer's last reported state**

```bash
mosquitto_sub -h localhost -v -t home/buzzer/status -C 1
```

```
home/buzzer/status ON
```

**Example 2: watch everything about the buzzer** (press `Ctrl+C` to stop)

```bash
mosquitto_sub -h localhost -v -t 'home/buzzer/#'
```

Then, in a second terminal window, send a good command and a bad one:

```bash
mosquitto_pub -h localhost -t home/buzzer -m ON
mosquitto_pub -h localhost -t home/buzzer -m BEEP
```

The first window shows:

```
home/buzzer ON
home/buzzer/status ON
home/buzzer BEEP
home/buzzer/error {"error": "Invalid command: BEEP. Use ON or OFF.", "timestamp": "...", "topic": "home/buzzer"}
```

In order: the command you sent, the Pi's reply, the bad command, and the Pi's
error. **Errors like this only appear here, not in the log**, so watch the
`/error` topic when a command seems to do nothing.

**Good to know**
- Put quotes around topics that contain `#`, like `'home/#'`.
- `mosquitto_sub -h localhost -v -t 'home/#'` shows every message in the house.

---

## Checklist

Copy this for each new device.

**Wiring**
- [ ] Step 1: Device wired to a free pin, with the Pi switched off

**Raspberry Pi: `mqttlistener.py`**
- [ ] Step 3: Pin name, for example `BUZZER_PIN = 5`
- [ ] Step 4: Topic name, for example `TOPIC_BUZZER = "home/buzzer"`
- [ ] Step 5: State in `device_states`, **with a comma on the line above**
- [ ] Step 6: `GPIO.setup()` in `setup_gpio()`
- [ ] Step 7: Topic added to the `for topic in [...]` list
- [ ] Step 8: `control_...()` function
- [ ] Step 9: `elif topic == ...` block in `on_message()`
- [ ] Step 10: Switched off in `cleanup_and_exit()`
- [ ] Step 11: `py_compile` prints nothing
- [ ] Step 12: Log shows `Subscribed to: home/...`
- [ ] Step 13: Works with `mosquitto_pub`

**iPad app**
- [ ] Step 15: `@Published` state in `Models.swift`
- [ ] Step 16: `toggle...()` function in `MQTTClient.swift`
- [ ] Step 17: Undo line in `publishCommand()`
- [ ] Step 18: `DeviceCard` in `DeviceControlsSection.swift`
- [ ] Step 19: Badge number and `activeDevicesCount` updated
- [ ] Step 20 (optional): Topic added to the `topics` list
- [ ] Step 21: Card works from the iPad

---

## Troubleshooting

**Always test in this order:** wiring, then `mosquitto_pub`, then the app. Each test
rules out one whole part of the system.

### On the Raspberry Pi

| What you see | Where | Cause and fix |
|---|---|---|
| `SyntaxError: invalid syntax. Perhaps you forgot a comma?` | `py_compile` | Missing comma, usually after `"door":   False` in Step 5 |
| `IndentationError: ...` | `py_compile` | Spaces at the start of a line do not match the lines around it |
| `Fatal error: name 'BUZZER_PIN' is not defined` | log | Step 3 missing, or the name is spelled differently somewhere |
| No `Subscribed to: home/buzzer` line | log | Step 7: topic not added to the `for topic in` list |
| Nothing at all in the log when you send a command | log | Topic spelled differently in your command or the app. Topics are case sensitive |
| `Message on unknown topic: home/buzzer` | log | Step 9: the `elif` block is missing or its topic name is different |
| `Message handling error: name 'control_buzzer' is not defined` | log | Step 8: function missing, or its name does not match Step 9 |
| `home/buzzer/error {"error": "Invalid command: ..."}` | `mosquitto_sub` | You sent a word other than `ON` or `OFF` |
| Log says `Doorbell Buzzer → ON` but it is silent | log | Wiring, wrong pin number, or a passive buzzer. Check Step 1 |
| Another device stopped working | | Two devices on the same GPIO pin |
| `Active: failed` | `systemctl status` | Read the log with `journalctl`. If you are stuck, restore your backup (see [Before you start](#before-you-start)) |

### In the iPad app

| What you see | Cause and fix |
|---|---|
| `value of type 'DeviceStates' has no member 'buzzerOn'` | Step 15: state missing from `Models.swift`, or spelled differently |
| `has no dynamic member 'toggleBuzzer'` or `cannot call value of non-function type 'Binding<Subject>'` | Step 16: `toggleBuzzer()` missing or spelled differently. The second message is confusing, but it means the same thing |
| No Doorbell card | Step 18 |
| Badge says `/3 Active` or the count is wrong | Step 19 |
| `Not connected - cannot control Doorbell Buzzer` | The app is not connected to the house. Connect first |
| Card turns on but the buzzer is silent | Test the Pi with `mosquitto_pub` (Step 13). If that works, check the topic spelling in Step 16 matches Step 4 exactly |
| Card turns on, then flips back off | The message could not be sent. Check the app is connected |

---

## Motors: DC and stepper

Motors are the one extension that needs more than a wire and a resistor. They are
worth doing, but read this section before buying parts.

The garage door used a 28BYJ-48 stepper motor in an earlier version of this
project, and was changed to a servo. A servo needs one pin, no driver board and no
separate power supply. Adding a motor back means taking on that extra work on
purpose, which makes it a good extension.

### Why a motor cannot go straight on a GPIO pin

| Component | Rough current |
|---|---|
| LED | 10 mA |
| SG90 servo, moving | 100 to 250 mA |
| 28BYJ-48 stepper | 200 mA or more |
| Small DC motor, stalled | 1 A or more |

A GPIO pin can supply about **16 mA**, and all the pins together about **50 mA**.
Connecting a motor directly will not work, and can damage the Pi. Every motor needs:

1. **Its own power supply**, with its ground wire also connected to a Pi GND pin.
   This shared ground is essential. Without it, the Pi and the motor driver
   disagree about what 0V is, and nothing works.
2. **A driver**: a transistor, Darlington array or H-bridge board. It lets a tiny
   GPIO signal switch a much bigger current.

### Option A: DC motor

Simplest to spin, but there is no position control. It spins while powered and
coasts to a stop.

- **One direction, on or off:** one transistor (a 2N2222 for a very small motor,
  or a logic-level MOSFET) plus a **flyback diode** across the motor's terminals.
  The diode is not optional. A motor makes a reverse voltage spike when it is
  switched off, which will eventually destroy the transistor.
- **Both directions:** an H-bridge board such as an L298N, DRV8833 or TB6612FNG.
  Two GPIO pins choose the direction, and a third controls speed with PWM.

Speed control uses the same PWM idea as the servos, but the number means power,
not position. A fan on GPIO 12 needs four pieces:

```python
# 1. Near the top, next to the other pins:
FAN_PIN = 12

# 2. Next to the line GARAGE_SERVO_PWM = None:
FAN_PWM = None
```

```python
    # 3. Inside setup_gpio(), after the other GPIO.setup lines (4 spaces):
    global FAN_PWM
    GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)
    FAN_PWM = GPIO.PWM(FAN_PIN, 1000)   # 1000 Hz suits a motor; 50 Hz would judder
    FAN_PWM.start(0)
```

```python
# 4. In Section 5, next to your other control functions:
def control_fan(speed: int) -> bool:
    """Set the fan speed. speed is 0 to 100 percent."""
    try:
        FAN_PWM.ChangeDutyCycle(speed)
        logger.info(f"Fan → {speed}%")
        return True
    except Exception as e:
        logger.error(f"Fan control error: {e}")
        return False
```

Then add the topic, the state and the subscription as in Steps 4, 5 and 7, and
send the fan a number instead of `ON` or `OFF`. See
[A device with a range](#a-device-with-a-range-not-just-on-and-off) for the
`elif` block.

### Option B: Stepper motor

A stepper moves an exact number of steps, but nothing tells it if it gets stuck.
This is called *open-loop* control. If the door jams, the Pi has no idea.

A 28BYJ-48 with a ULN2003 driver board is the usual classroom choice. It needs
**four GPIO pins**, one for each coil, because the Pi switches the coils itself.

There is a ready-made test script:

```bash
cd ~/simpsons-house
sudo systemctl stop simpsons-house.service
mqttenv/bin/python extensions/stepper_test.py
```

It uses GPIO 5, 6, 13 and 19, and turns the motor one full turn each way. Read the
comment at the top of the file first: it has the wiring and the power warning.
Start the house again afterwards with `sudo systemctl start simpsons-house.service`.

To control a stepper from the iPad, put the stepping code in a control function
and call it from an `elif` block, exactly like Steps 8 and 9. **Keep each move
short.** While `on_message()` is busy turning the motor, the house cannot respond
to any other command.

---

## Harder extensions

### A device with a range, not just on and off

An LED with adjustable brightness, or a fan with adjustable speed, needs a number
rather than `ON` or `OFF`:

```bash
mosquitto_pub -h localhost -t home/fan -m 75
```

In `on_message()`, turn the message into a number and check it:

```python
        elif topic == TOPIC_FAN:
            device_name = "Fan"
            try:
                level = int(payload)
            except ValueError:
                publish_error(topic, f"Invalid level: {payload}. Use 0-100.")
                return
            if not 0 <= level <= 100:
                publish_error(topic, "Level must be 0-100.")
                return
            success = control_fan(level)
            command_state = level > 0
```

The last line sets `command_state` to `True` when the fan is on at any speed. The
code after the `if` chain uses it to report the state.

In the app, a `Slider` replaces the on/off button. `DeviceCard` only understands on
and off, so make your own card. `GarageDoorCard.swift` is already a custom card and
is a good file to copy.

### A sensor instead of an output

A motion sensor or a button sends information **into** the Pi, so the pin is set up
with `GPIO.IN` instead of `GPIO.OUT`. When it changes, the Pi publishes a message,
for example to `home/motion/status`. Look at `publish_device_status()` in
Section 6 to see how the Pi publishes.

You can watch the sensor's messages with:

```bash
mosquitto_sub -h localhost -v -t 'home/motion/#'
```

**Showing it in the app is a much bigger challenge.** The app currently only sends
messages and never subscribes to any topic, so it cannot receive anything from the
Pi. You would need to add an MQTT SUBSCRIBE packet to `MQTTClient.swift`, and then
read incoming PUBLISH packets where it currently only logs
`House status update received`.

### More ideas

- A porch light on a second LED
- An RGB LED using three PWM pins
- A reed switch that detects whether the front door is really shut
- A temperature sensor in the roof

---

## See also

- `WIRING_GUIDE.md`: identifying components and breadboard layout
- `SERVO_TUNING_GUIDE.md`: setting door positions with `servo_calibrate.py`
- `TEACHING_GUIDE.md`: how a tap on the iPad becomes movement on the Pi
- `README.md`: *Getting the latest version* (`git pull`)

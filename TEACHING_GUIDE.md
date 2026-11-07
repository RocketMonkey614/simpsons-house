# Teaching Guide — Chromebook coding project

**Years 9–10 Digital Technologies | Term 1 | Simpson's House**

Students develop and personalise a browser controller for their own model house. The [Chromebook starter](chromebook-app/) deliberately has incomplete features and a small logic bug. It is a coding task, not a finished control page. The supplied [house-transport.js](chromebook-app/house-transport.js) handles MQTT packets so students can focus on algorithms, state, debugging, testing, and interface design. The older Swift Playgrounds zip remains an Apple-device example.

## Teacher setup

Each student or group should have a separate copy of [chromebook-app/](chromebook-app/). A shared Pi-hosted copy is suitable for demonstration, but students editing one shared copy would overwrite each other's work. Use a school-approved editor and local HTTP server on each Chromebook where the ChromeOS Linux development environment is enabled. From the folder containing the student copy:

~~~bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory chromebook-app
~~~

Open **http://localhost:8000** in Chrome, enter the Pi's IP address, and select **Connect to House**. If Linux development is unavailable on managed Chromebooks, arrange an approved way to serve each student's files over local HTTP. A teacher can demonstrate from the Pi with:

~~~bash
cd ~/simpsons-house
python3 -m http.server 8000 --bind 0.0.0.0 --directory chromebook-app
~~~

Open **http://PI_IP_ADDRESS:8000** on a Chromebook. Find the Pi's address with **hostname -I**. The Pi must have been configured with [setup.sh](setup.sh), and the house service and Mosquitto must be running. The Chromebook must reach the Pi on port **9001** for MQTT over WebSocket. Pi-hosted pages additionally require port **8000**. School Wi-Fi isolation may prevent this; check with the network administrator.

Serve the page using HTTP. An HTTPS-hosted coding site cannot connect to the Pi's insecure WebSocket at **ws://PI_IP_ADDRESS:9001** in Chrome. The Pi setup allows anonymous MQTT clients, so keep this activity on a trusted classroom network.

## The intended student starting point

| Part | Starting behaviour | Student work |
|---|---|---|
| Connection and MQTT | Supplied in [house-transport.js](chromebook-app/house-transport.js) | Explain the message path; leave packet encoding alone. |
| Light | Commands and status work | Use as the example to trace. |
| Active badge | Always says 0/3 | Implement a counting function. |
| Garage | Open works; Close sends the wrong payload | Trace and fix the logic bug. |
| Device statuses | Only the light updates on screen | Add validated garage and door handling. |
| Front door | Card has no control buttons | Add accessible buttons with the correct attributes. |
| Appearance | Plain working layout | Design and justify changes for the student's house. |

The intentional gaps are in [app.js](chromebook-app/app.js) and [index.html](chromebook-app/index.html). The CSS in [styles.css](chromebook-app/styles.css) is ready for student changes. There is no hidden dependency or external JavaScript library.

## Learning sequence

### 1. Define and design

Interview the intended user of the model house. Record at least three functional requirements, such as “the user can close the garage” and “the page shows the last confirmed door status,” and two non-functional requirements, such as readable contrast or clear error feedback. Sketch a card layout and draw the message path: Chromebook → Wi-Fi → Mosquitto → Python listener → GPIO → status reply. Explain why the browser sends data rather than driving GPIO itself.

### 2. Trace before editing

In [app.js](chromebook-app/app.js), find the button click handler, **sendCommand()**, **commandFor()**, and **updateDeviceStatus()**. Use the light as a known working example. On the Pi, run:

~~~bash
mosquitto_sub -h localhost -t 'home/#' -v
~~~

Predict the topic and payload for each button before clicking it. Compare your prediction with the Activity list and the Pi terminal. The backend in [mqttlistener.py](mqttlistener.py) accepts **OPEN** and **CLOSE** for the garage; it uses **ON** and **OFF** for the front door.

### 3. Complete the core algorithms

- **Task 1 — Active count:** Replace the placeholder in **countActiveDevices()**. Count only devices with a confirmed active state. Unknown and inactive devices do not count. Use a loop so the algorithm can be described in pseudocode.
- **Task 2 — Garage bug:** Repair **commandFor()** so Close produces the exact payload the Pi accepts. Submit a short trace showing the input, returned payload, and observed result before and after the fix.
- **Task 3 — Status handling:** Extend **updateDeviceStatus()** for the garage and front door. Validate topic and payload before changing **deviceStates** or the displayed text. Ignore unrelated topics and invalid payloads.
- **Task 4 — Front door:** Add Open and Close buttons in [index.html](chromebook-app/index.html). Use **data-device="door"** and **data-action="open"** or **"close"**. Start them disabled so they cannot send before connection.

The browser must display **Unknown** until a status message arrives. Sending a command does not prove the device moved. Only a status reply should change the displayed state.

### 4. Personalise and evaluate

Change headings, labels, colours, layout, and status presentation to suit the group's house and user. Keep content in [index.html](chromebook-app/index.html), presentation in [styles.css](chromebook-app/styles.css), and behaviour in [app.js](chromebook-app/app.js). Test keyboard use, button clarity, and whether a user can tell **sent** from **confirmed**. Explain two design decisions using the user's requirements.

### 5. Year 10 bridge to Python

ATAR Computer Science uses Python for examination programming questions. After completing the JavaScript algorithms, translate **commandFor()** and **countActiveDevices()** into [python_bridge.py](chromebook-app/python_bridge.py). Run the provided known-answer tests on the Pi or a Chromebook with Python:

~~~bash
python3 -m unittest discover -s chromebook-app -p 'test_python_bridge.py'
~~~

The tests in [test_python_bridge.py](chromebook-app/test_python_bridge.py) are **expected to fail in the starter**. They cover every valid command, unknown commands, zero and all-active states, and an unknown state. Students should explain which ideas transfer between JavaScript and Python: functions, parameters, selection, iteration, dictionaries/objects, Booleans, and test cases. This Python exercise does not control hardware.

## Suggested test evidence

| Test | Expected result |
|---|---|
| Before connection | Control buttons disabled; device states Unknown; badge 0/3. |
| Light ON status received | Light shows ON; badge rises by one. |
| Garage CLOSE clicked | MQTT payload is exactly CLOSE; Pi reports CLOSED. |
| Garage OPEN status received | Garage shows OPEN; badge rises by one. |
| Front door Open clicked | Topic home/door carries ON; status reply changes door display. |
| Invalid status payload or unrelated topic | No displayed device state changes. |
| Disconnect | Controls disabled; last reported states remain visible as last known values. |
| Keyboard navigation | Every active control can be reached and used without a mouse. |

For each test, record input, predicted output, actual output, and any correction. Use at least one trace table or pseudocode algorithm in the submission. Students should distinguish a syntax error, a runtime error, and a logic error using examples encountered in their work.

## Curriculum alignment

This sequence uses the **WA Digital Technologies curriculum for implementation in 2026**. The [SCSA scope and sequence](https://k10outline.scsa.wa.edu.au/__data/assets/pdf_file/0003/1228575/Technologies-Digital-Technologies-Scope-and-sequence-of-the-mandated-curriculum-content-For-implementation-in-2026.PDF) includes the following progression:

| Focus | Year 9 evidence | Year 10 extension |
|---|---|---|
| Problem and UX | Gather end-user needs and prototype the controls. | Define client needs and justify interface decisions. |
| Algorithms | Design functions in pseudocode or a flow chart; predict and compare outcomes for test cases. | Design modular algorithms with functions and logical operators; validate across a range of cases. |
| Programming | Implement, modify, and debug functions in a general-purpose language. | Apply modular algorithms and data structures; translate the logic into Python. |
| Digital systems and data | Explain how browser, network, broker, Pi software, and GPIO exchange data; keep HTML, CSS, and JavaScript separate. | Discuss reliability, access control, and risks of anonymous local MQTT. |
| Evaluation | Test against user requirements and reflect on improvements. | Use test evidence and stakeholder feedback to refine the solution. |

This is a teaching alignment, not an official assessment rubric. The [2026 Year 11 Computer Science ATAR syllabus](https://senior-secondary.scsa.wa.edu.au/__data/assets/pdf_file/0020/1232507/Computer-Science-ATAR-Year-11-Syllabus-for-teaching-from-2026.PDF) prescribes **Python** for programming examination questions. Its Unit 1 includes sequence, selection, iteration, functions with parameters, arrays, pseudocode, testing, debugging, and network communications. JavaScript provides a useful browser project context; the Python bridge gives students direct practice in the prescribed language.

## Suggested assessment evidence

Collect the requirements and sketch, an algorithm in pseudocode, the student's edited files, a before-and-after bug trace, a test table, and a short evaluation against the requirements. For Year 10, include the Python translation and test results. Judge the quality of reasoning and test evidence as well as the final appearance.

## Troubleshooting

**The page does not load:** Check that the HTTP server is running and that the Chromebook opened the correct address and port 8000.

**Connect fails:** Check the Pi IP, network reachability, and **sudo systemctl status mosquitto**. The WebSocket listener uses port 9001.

**A command appears as Sent but no status arrives:** Check **sudo systemctl status simpsons-house** and the Pi's MQTT traffic. The transport may be connected while the Python listener is stopped.

**The badge or garage is wrong:** Those are intentional starter tasks. Trace the data through [app.js](chromebook-app/app.js) before changing the Pi code.

**The Python tests fail before students begin:** That is expected. [python_bridge.py](chromebook-app/python_bridge.py) contains unfinished functions.

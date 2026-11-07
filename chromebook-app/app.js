// STUDENT FILE — build and debug the control page for your own model house.
// The MQTT packet code is supplied in house-transport.js. Work on the
// algorithms, state, user interface and tests here.
const hostInput = document.querySelector("#pi-host");
const connectButton = document.querySelector("#connect");
const connectionStatus = document.querySelector("#connection-status");
const activity = document.querySelector("#activity");
const commandButtons = document.querySelectorAll("button[data-device]");
const activeCount = document.querySelector("#active-count");

// null means no status has been received yet.
const deviceStates = { light: null, garage: null, door: null };
let connected = false;
hostInput.value = location.hostname || localStorage.getItem("simpsons-pi-host") || "";

function log(message) {
  const item = document.createElement("li");
  item.textContent = new Date().toLocaleTimeString() + " — " + message;
  activity.prepend(item);
  while (activity.children.length > 30) activity.lastChild.remove();
}

function setConnection(message, isConnected) {
  connected = isConnected;
  connectionStatus.textContent = message;
  connectButton.textContent = isConnected ? "Disconnect" : "Connect to House";
  for (const button of commandButtons) button.disabled = !isConnected;
}

// TASK 1 — The badge always says 0/3. Count true values in deviceStates.
// Unknown (null) and inactive (false) must not be counted.
function countActiveDevices() {
  return 0; // TODO: replace this placeholder with an algorithm using iteration
}

function showActiveCount() {
  activeCount.textContent = countActiveDevices() + "/3 Active";
}

// TASK 2 — The garage CLOSE button does not work. Trace the topic and payload
// in Activity and compare the payload with mqttlistener.py. Fix the mapping.
// Do not change the words on the buttons: those are for users.
function commandFor(device, action) {
  const commands = {
    light: { on: "ON", off: "OFF" },
    garage: { open: "OPEN", close: "CLOSED" }, // Deliberate logic bug
    door: { open: "ON", close: "OFF" }
  };
  return commands[device]?.[action] ?? null;
}

function sendCommand(device, action) {
  const command = commandFor(device, action);
  if (command === null) {
    log("No command for " + device + " / " + action);
    return;
  }
  const topic = "home/" + device;
  if (transport.publish(topic, command)) {
    log("Sent " + topic + " → " + command);
  } else {
    log("Connect to the house before sending a command");
  }
}

// TASK 3 — Only the light status is displayed. Extend this function to
// validate and display garage and front-door status messages too.
// Expected topics: home/light/status, home/garage/status, home/door/status.
// Expected values: ON/OFF for light and door; OPEN/CLOSED for garage.
// Ignore unrelated topics. Update deviceStates, then call showActiveCount().
function updateDeviceStatus(topic, message) {
  if (topic === "home/light/status" && (message === "ON" || message === "OFF")) {
    deviceStates.light = message === "ON";
    document.querySelector("#light-status").textContent = message;
    showActiveCount();
  }
}

function receiveMessage(topic, message) {
  log("Received " + topic + " → " + message);
  if (topic.endsWith("/error")) return; // The error is visible in Activity.
  updateDeviceStatus(topic, message);
}

const transport = new HouseTransport({
  onConnection: setConnection,
  onMessage: receiveMessage,
  onLog: log
});

connectButton.addEventListener("click", () => {
  if (connected) {
    transport.disconnect();
    return;
  }
  const host = hostInput.value.trim();
  if (!host) {
    setConnection("Enter the Pi address", false);
    return;
  }
  try {
    localStorage.setItem("simpsons-pi-host", host);
    transport.connect(host);
  } catch (error) {
    setConnection(error.message, false);
  }
});

// TASK 4 — Add front-door buttons in index.html with data-device="door"
// and data-action="open" or "close". This handler will then work for them.
for (const button of commandButtons) {
  button.addEventListener("click", () => {
    sendCommand(button.dataset.device, button.dataset.action);
  });
}

showActiveCount();

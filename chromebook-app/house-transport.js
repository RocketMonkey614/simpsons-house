// Teacher-supplied MQTT transport. Student tasks belong in app.js.
// Chrome provides WebSocket; this file encodes and decodes MQTT 3.1.1 packets.
class HouseTransport {
  constructor({ onConnection, onMessage, onLog }) {
    this.onConnection = onConnection;
    this.onMessage = onMessage;
    this.onLog = onLog;
    this.socket = null;
    this.pingTimer = null;
    this.packetId = 0;
    this.connected = false;
    this.encoder = new TextEncoder();
    this.decoder = new TextDecoder();
  }

  mqttString(value) {
    const bytes = this.encoder.encode(value);
    if (bytes.length > 65535) throw new Error("MQTT string is too long");
    return [bytes.length >> 8, bytes.length & 255, ...bytes];
  }

  packet(header, body) {
    const length = [];
    let remaining = body.length;
    do {
      let digit = remaining % 128;
      remaining = Math.floor(remaining / 128);
      if (remaining) digit |= 128;
      length.push(digit);
    } while (remaining);
    return new Uint8Array([header, ...length, ...body]);
  }

  connect(host) {
    this.disconnect();
    if (!/^[a-zA-Z0-9.-]+$/.test(host)) throw new Error("Invalid Pi address");
    if (location.protocol === "https:") throw new Error("Open the page over HTTP to use the Pi WebSocket");
    const currentSocket = new WebSocket("ws://" + host + ":9001/", "mqtt");
    this.socket = currentSocket;
    currentSocket.binaryType = "arraybuffer";
    this.onConnection("Connecting…", false);

    currentSocket.addEventListener("open", () => {
      if (this.socket !== currentSocket) return;
      const clientId = "chromebook-" + Math.random().toString(36).slice(2, 10);
      currentSocket.send(this.packet(0x10, [
        ...this.mqttString("MQTT"), 4, 2, 0, 60, ...this.mqttString(clientId)
      ]));
    });
    currentSocket.addEventListener("message", event => {
      if (this.socket !== currentSocket) return;
      try { this.readPackets(new Uint8Array(event.data)); }
      catch (error) { this.onLog("Packet error: " + error.message); }
    });
    currentSocket.addEventListener("error", () => {
      if (this.socket === currentSocket) this.onLog("WebSocket error; check the Pi address and port 9001");
    });
    currentSocket.addEventListener("close", () => {
      if (this.socket !== currentSocket) return;
      clearInterval(this.pingTimer);
      this.pingTimer = null;
      this.socket = null;
      this.connected = false;
      this.onConnection("Disconnected", false);
      this.onLog("Connection closed");
    });
  }

  disconnect() {
    clearInterval(this.pingTimer);
    this.pingTimer = null;
    const oldSocket = this.socket;
    this.socket = null;
    this.connected = false;
    if (oldSocket && oldSocket.readyState === WebSocket.OPEN) {
      oldSocket.send(new Uint8Array([0xe0, 0]));
    }
    if (oldSocket) oldSocket.close();
    this.onConnection("Disconnected", false);
  }

  subscribe(topic) {
    this.packetId = (this.packetId % 65535) + 1;
    this.socket.send(this.packet(0x82, [
      this.packetId >> 8, this.packetId & 255, ...this.mqttString(topic), 0
    ]));
  }

  publish(topic, command) {
    if (!this.connected || !this.socket || this.socket.readyState !== WebSocket.OPEN) return false;
    this.socket.send(this.packet(0x30, [...this.mqttString(topic), ...this.encoder.encode(command)]));
    return true;
  }

  readPackets(bytes) {
    let position = 0;
    while (position < bytes.length) {
      const header = bytes[position++];
      let length = 0;
      let multiplier = 1;
      let digit;
      do {
        if (position >= bytes.length || multiplier > 128 * 128 * 128) throw new Error("Invalid MQTT length");
        digit = bytes[position++];
        length += (digit & 127) * multiplier;
        multiplier *= 128;
      } while (digit & 128);
      if (position + length > bytes.length) throw new Error("Incomplete MQTT packet");
      this.handlePacket(header, bytes.subarray(position, position + length));
      position += length;
    }
  }

  handlePacket(header, body) {
    const kind = header >> 4;
    if (kind === 2) { // CONNACK
      if (body.length < 2 || body[1] !== 0) {
        this.onLog("Broker refused connection");
        if (this.socket) this.socket.close();
        return;
      }
      this.connected = true;
      this.onConnection("Connected to the Raspberry Pi", true);
      for (const device of ["light", "garage", "door"]) {
        this.subscribe("home/" + device + "/status");
        this.subscribe("home/" + device + "/error");
      }
      this.pingTimer = setInterval(() => {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          this.socket.send(new Uint8Array([0xc0, 0]));
        }
      }, 25000);
      this.onLog("Connected; waiting for device status");
    } else if (kind === 3) { // PUBLISH
      if (body.length < 2) return;
      const topicLength = (body[0] << 8) | body[1];
      let offset = 2 + topicLength;
      if (offset > body.length) return;
      const topic = this.decoder.decode(body.subarray(2, offset));
      if ((header & 6) !== 0) offset += 2;
      if (offset > body.length) return;
      const message = this.decoder.decode(body.subarray(offset));
      this.onMessage(topic, message);
    }
  }
}

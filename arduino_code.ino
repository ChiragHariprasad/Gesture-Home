const int relayPins[] = {2, 3, 4, 5}; // Relay pins
const int numRelays = sizeof(relayPins) / sizeof(relayPins[0]);

void setup() {
  Serial.begin(9600); // Initialize serial communication

  // Set relay pins as outputs and initialize them to OFF
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH); // HIGH is OFF for active-low relays
  }
}

void toggleRelay(int relayIndex) {
  if (relayIndex >= 0 && relayIndex < numRelays) {
    // Read the current state of the relay
    int currentState = digitalRead(relayPins[relayIndex]);
    // Toggle the state
    digitalWrite(relayPins[relayIndex], !currentState);
  }
}

void loop() {
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();

    // Check if the received char is a digit
    if (isdigit(receivedChar)) {
      int fingerCount = receivedChar - '0'; // Convert char to integer

      // Toggle the corresponding relay
      if (fingerCount >= 1 && fingerCount <= numRelays) {
        toggleRelay(fingerCount - 1); // Index starts from 0, so subtract 1
      }
    }
  }
}

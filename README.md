# GestureHome

GestureHome is a home automation system designed for verbally disabled individuals, enabling control of household appliances using hand gestures captured through a webcam. It uses Python for gesture recognition and Arduino for controlling relays connected to home devices.

## Features
- **Gesture Recognition**: Detects hand gestures and counts the number of extended fingers using a webcam.
- **Relay Control**: Controls connected appliances based on gestures.
- **Hold Gesture Confirmation**: Prevents accidental toggling by requiring gestures to be held for a defined time.
- **Arduino Communication**: Efficient communication between Python and Arduino for seamless relay control.

## Hardware Requirements
- Arduino board (e.g., Arduino Uno)
- Relays (connected to pins 2, 3, 4, and 5)
- Webcam
- Computer with Python installed

## Setup

### Arduino
1. Connect relays to pins 2, 3, 4, and 5 on the Arduino board.
2. Upload the provided `arduino_code.ino` sketch to the board.

### Python Environment
1. Install Python 3.x.
2. Set up a virtual environment and install dependencies:
   ```bash
   pip install opencv-python numpy pyserial
   ```
3. Connect the Arduino to the computer and note the COM port.

### Run the System
1. Modify the COM port in the Python script (`main.py`) to match your Arduino's port.
2. Run the Python script:
   ```bash
   python main.py
   ```
3. Show gestures in front of the webcam to control the relays.

## Use Case
This system is designed to assist verbally disabled individuals in controlling household appliances independently by using simple hand gestures.

## Future Enhancements
- Add support for more gestures and functionalities.
- Integrate a mobile app for monitoring relay states.
- Implement voice-to-gesture translation for hybrid accessibility.

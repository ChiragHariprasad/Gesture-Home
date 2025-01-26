import cv2
import numpy as np
import math
import serial
import time


def calculate_finger_count(cnt, defects):
    if defects is None:
        return 0

    count_defects = 0
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])

        # Calculate triangle sides
        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

        # Calculate angle
        if b * c == 0:  # Prevent division by zero
            continue

        angle = math.degrees(math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)))

        # Refined angle threshold for better accuracy
        if angle <= 90 and d > 10000:  # Added depth threshold
            count_defects += 1

    # Adjust finger count based on defects
    return count_defects + 1


try:
    # Attempt to connect to Arduino
    print("Connecting to Arduino...")
    arduino = serial.Serial('COM5', 9600, timeout=2)  # Add timeout for better error handling
    time.sleep(2)  # Wait for the connection to stabilize
    print("Arduino connected successfully!")
except serial.SerialException as e:
    print(f"SerialException: Could not open port. Error: {e}")
    arduino = None
except Exception as e:
    print(f"General Error: {e}")
    arduino = None

if arduino:
    print("Testing communication...")
    arduino.write(b'1')  # Test signal
    arduino.write(b'1')  # Toggle 1
else:
    print("Running in debug mode")

# Initialize video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Create named windows first
cv2.namedWindow('Gesture')
cv2.namedWindow('Contours')
cv2.namedWindow('Thresholded')

# State variables
palm_hold_time = 0
palm_start_time = None
finger_hold_time = 0
finger_start_time = None
last_finger_count = None
current_state = "DETECT_PALM"  # States: DETECT_PALM, COUNT_FINGERS
HOLD_DURATION = 3  # Seconds to hold for confirmation

while True:
    ret, img = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        break

    # Define ROI (keeping your original coordinates)
    roi = (100, 100, 300, 300)
    cv2.rectangle(img, (roi[0], roi[1]), (roi[2], roi[3]), (0, 255, 0), 2)

    # Crop image
    crop_img = img[roi[1]:roi[3], roi[0]:roi[2]]

    # Image processing
    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(grey, (35, 35), 0)
    _, thresh1 = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(thresh1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    finger_count = 0
    status_text = "No hand detected"

    if contours and len(contours) > 0:
        # Get largest contour
        cnt = max(contours, key=cv2.contourArea)

        # Minimum contour area threshold
        if cv2.contourArea(cnt) > 10000:
            hull = cv2.convexHull(cnt, returnPoints=False)
            defects = cv2.convexityDefects(cnt, hull)

            # Calculate finger count
            finger_count = calculate_finger_count(cnt, defects)

            # State machine logic
            if current_state == "DETECT_PALM":
                if finger_count >= 4:  # Open palm detected
                    if palm_start_time is None:
                        palm_start_time = time.time()

                    palm_hold_time = time.time() - palm_start_time
                    if palm_hold_time >= HOLD_DURATION:
                        current_state = "COUNT_FINGERS"
                        if arduino:
                            arduino.write(b'S')  # Signal state change to Arduino
                        finger_start_time = None
                        last_finger_count = None
                        status_text = f"Palm detected! Show fingers now."
                    else:
                        status_text = f"Hold palm open: {HOLD_DURATION - int(palm_hold_time)}s"
                else:
                    palm_start_time = None
                    status_text = "Show open palm"

            elif current_state == "COUNT_FINGERS":
                if last_finger_count != finger_count:
                    finger_start_time = time.time()
                    last_finger_count = finger_count
                    finger_hold_time = 0
                else:
                    finger_hold_time = time.time() - finger_start_time
                    if finger_hold_time >= HOLD_DURATION:
                        if arduino:
                            arduino.write(str(finger_count).encode())
                            print(f"Sent to Arduino: {finger_count}")  # Debug print
                            time.sleep(0.5)  # Prevent rapid toggling

                        # After sending the signal, return to DETECT_PALM state
                        current_state = "DETECT_PALM"
                        palm_start_time = None
                        finger_start_time = None
                        last_finger_count = None  # Reset the last finger count to prevent unintentional repeats
                        status_text = "Command sent! Show palm to reset."
                    else:
                        status_text = f"Hold fingers {finger_count}: {HOLD_DURATION - int(finger_hold_time)}s"

            # Draw contours
            drawing = np.zeros(crop_img.shape, np.uint8)
            cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 2)
            cv2.drawContours(drawing, [cv2.convexHull(cnt)], 0, (0, 0, 255), 2)

            # Show combined image
            all_img = np.hstack((drawing, crop_img))
            cv2.imshow('Contours', all_img)

    # Display results
    cv2.putText(img, status_text, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow('Gesture', img)
    cv2.imshow('Thresholded', thresh1)

    # Check for window closing or ESC key
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or cv2.getWindowProperty('Gesture', cv2.WND_PROP_VISIBLE) < 1:
        break

# Cleanup
if arduino:
    arduino.close()
cap.release()
cv2.destroyAllWindows()

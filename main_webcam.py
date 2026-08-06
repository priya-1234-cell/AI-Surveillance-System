from ultralytics import YOLO
import cv2
import csv
import os
from datetime import datetime

# -----------------------------
# Load YOLO Model
# -----------------------------
model = YOLO("yolov8n.pt")

# -----------------------------
# Open Video
# -----------------------------
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("❌ Webcam not found!")
    exit()

# -----------------------------
# Restricted Zone Coordinates
# -----------------------------
ZONE_X1 = 10
ZONE_Y1 = 380
ZONE_X2 = 720
ZONE_Y2 = 720

# -----------------------------
# Create Output Folders
# -----------------------------
os.makedirs("outputs/images", exist_ok=True)
os.makedirs("outputs/logs", exist_ok=True)

# -----------------------------
# CSV Log File
# -----------------------------
log_file = "outputs/logs/intrusion_log.csv"

if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Time", "Person ID", "Event"])

# -----------------------------
# Variables
# -----------------------------
alerted_ids = set()

show_banner = False
banner_text = ""
# -----------------------------
# Main Loop
# -----------------------------
cv2.namedWindow("AI Surveillance", cv2.WINDOW_NORMAL)
cv2.resizeWindow("AI Surveillance", 1280, 720)
cv2.setWindowProperty("AI Surveillance", cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Detect & Track People
    results = model.track(
        frame,
        persist=True,
        tracker="botsort.yaml",
        classes=[0],
        conf=0.7,
        verbose=False
    )

    annotated_frame = frame.copy()

    person_count = len(results[0].boxes)

    # Reset every frame
    intrusion_detected = False

    # -----------------------------
    # Process Every Person
    # -----------------------------
    for box in results[0].boxes:

        if box.id is None:
            continue

        track_id = int(box.id.item())

        # Bounding Box
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # Feet Position
        foot_x = (x1 + x2) // 2
        foot_y = y2

        # Check if inside restricted zone
        inside_zone = (
            ZONE_X1 < foot_x < ZONE_X2 and
            ZONE_Y1 < foot_y < ZONE_Y2
        )

        # -----------------------------
        # Box Colour
        # -----------------------------
        if inside_zone:
            box_color = (0, 0, 255)
            intrusion_detected = True
        else:
            box_color = (0, 255, 0)

            # Reset alert when person leaves
            if track_id in alerted_ids:
                alerted_ids.remove(track_id)

        # Draw Bounding Box
        cv2.rectangle(
            annotated_frame,
            (x1, y1),
            (x2, y2),
            box_color,
            2
        )

        # Draw ID
        cv2.putText(
            annotated_frame,
            f"ID {track_id}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            box_color,
            2
        )

        # Draw Foot Point
        cv2.circle(
            annotated_frame,
            (foot_x, foot_y),
            7,
            (0, 255, 255),
            -1
        )

        # -----------------------------
        # Intrusion Alert
        # -----------------------------
        if inside_zone and track_id not in alerted_ids:

            alerted_ids.add(track_id)

            print(f"🚨 ALERT! Person {track_id} entered the restricted zone!")

            now = datetime.now()

            # Save CSV Log
            with open(log_file, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    track_id,
                    "Intrusion Detected"
                ])

            # Save Screenshot
            image_name = (
                f"outputs/images/intrusion_{track_id}_"
                f"{now.strftime('%Y%m%d_%H%M%S')}.jpg"
            )

            cv2.imwrite(image_name, annotated_frame)

            # Show Banner
            show_banner = True
            banner_text = "INTRUSION DETECTED!"
                # -----------------------------
    # Restricted Zone Status
    # -----------------------------
    if intrusion_detected:
        zone_color = (0, 0, 255)
        zone_text = "RESTRICTED ZONE"
    else:
        zone_color = (0, 255, 0)
        zone_text = "SAFE ZONE"

    # Draw Restricted Zone
    cv2.rectangle(
        annotated_frame,
        (ZONE_X1, ZONE_Y1),
        (ZONE_X2, ZONE_Y2),
        zone_color,
        4
    )

    cv2.putText(
        annotated_frame,
        zone_text,
        (ZONE_X1, ZONE_Y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        zone_color,
        2
    )

    # -----------------------------
    # Alert Banner
    # -----------------------------
    if show_banner:

        cv2.rectangle(
            annotated_frame,
            (0, 0),
            (annotated_frame.shape[1], 80),
            (0, 0, 255),
            -1
        )

        cv2.putText(
            annotated_frame,
            banner_text,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            3
        )

    # Hide banner once everyone leaves the zone
    if not intrusion_detected:
        show_banner = False

    # -----------------------------
    # People Count
    # -----------------------------
    cv2.putText(
        annotated_frame,
        f"People Count: {person_count}",
        (20, annotated_frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    # -----------------------------
    # Display Video
    # -----------------------------
    annotated_frame = cv2.resize(annotated_frame, (1280, 720))
    cv2.imshow("AI Surveillance", annotated_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or cv2.getWindowProperty("AI Surveillance", cv2.WND_PROP_VISIBLE) < 1:
        break

# -----------------------------
# Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()

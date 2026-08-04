from ultralytics import YOLO
import cv2

# -----------------------------
# Load YOLO Model
# -----------------------------
model = YOLO("yolov8n.pt")

# -----------------------------
# Open Video
# -----------------------------
cap = cv2.VideoCapture("data/videos/sample.mp4")

# -----------------------------
# Restricted Zone Coordinates
# -----------------------------
ZONE_X1 = 0
ZONE_Y1 = 380

ZONE_X2 = 720
ZONE_Y2 = 720

# -----------------------------
# Main Loop
# -----------------------------
while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Detect and Track People
    results = model.track(
        frame,
        persist=True,
        classes=[0],
        conf=0.7,
        verbose=False
    )

    # Number of detected people
    person_count = len(results[0].boxes)

    # Draw YOLO detections
    annotated_frame = results[0].plot()

    # -----------------------------
    # Draw Restricted Zone
    # -----------------------------
    cv2.rectangle(
        annotated_frame,
        (ZONE_X1, ZONE_Y1),
        (ZONE_X2, ZONE_Y2),
        (0, 0, 255),
        3
    )

    cv2.putText(
        annotated_frame,
        "RESTRICTED ZONE",
        (ZONE_X1, ZONE_Y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )

    # -----------------------------
    # Check Every Person
    # -----------------------------
    for box in results[0].boxes:

        # Skip if tracking ID is not available
        if box.id is None:
            continue

        track_id = int(box.id.item())

        # Bounding Box Coordinates
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # Center of Bounding Box
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        print(track_id, center_x, center_y)

        # Draw Center Point
        cv2.circle(
            annotated_frame,
            (center_x, center_y),
            12,
            (0, 0, 255),
            -1
        )

        # Check if person entered restricted zone
        if (
            x1 < ZONE_X2
            and x2 > ZONE_X1
            and y1 < ZONE_Y2
            and y2 > ZONE_Y1
        ):
            print(f"🚨 ALERT! Person {track_id} entered the zone!")

            # Red Warning Banner
            cv2.rectangle(
                annotated_frame,
                (0, 0),
                (annotated_frame.shape[1], 100),
                (0, 0, 255),
                -1
            )

            # Alert Text
            cv2.putText(
                annotated_frame,
                f"INTRUSION DETECTED! PERSON ID {track_id}",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                3
            )

    # -----------------------------
    # Display People Count
    # -----------------------------
    cv2.putText(
        annotated_frame,
        f"People Count: {person_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    # -----------------------------
    # Show Video
    # -----------------------------
    cv2.imshow("AI Surveillance", annotated_frame)

    # Press Q to Quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# -----------------------------
# Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()
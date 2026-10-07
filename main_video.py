from ultralytics import YOLO
import cv2
import csv
import os
from datetime import datetime
from urllib.parse import quote
from src.alerts import send_intrusion_email


# ============================================================
# MODEL
# ============================================================

model = YOLO("yolov8n.pt")


# ============================================================
# CAMERA
# ============================================================

username = "admin"

password = os.getenv("CAMERA_PASSWORD")

if not password:
    password = input("Enter camera password: ")

password = quote(password, safe="")

rtsp_url = (
    f"rtsp://{username}:{password}"
    f"@192.168.1.6:554/video/live?channel=1&subtype=1"
)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"


cap = cv2.VideoCapture(
    rtsp_url,
    cv2.CAP_FFMPEG
)

if not cap.isOpened():
    print("CCTV video could not be opened!")
    exit()

print("CCTV video opened successfully")


# ============================================================
# SETTINGS
# ============================================================

ZONE_X1 = 10
ZONE_Y1 = 380
ZONE_X2 = 720
ZONE_Y2 = 720


# ============================================================
# LOITERING TIME
# ============================================================

# TESTING:
# Change this temporarily to 10 while testing.
#
# FINAL PROJECT:
# Keep this at 180 seconds.

LOITERING_TIME = 180


# ============================================================
# TRACKER GRACE PERIOD
# ============================================================

# YOLO can temporarily miss a person for a few frames.
# We do NOT immediately reset the loitering timer.
#
# If the person is not detected for this many seconds,
# we consider the zone empty.

ZONE_MISSING_GRACE = 2.0


# ============================================================
# VIDEO RECORDING
# ============================================================

RECORDING_DURATION = 10


# ============================================================
# OUTPUTS
# ============================================================

os.makedirs(
    "outputs/images",
    exist_ok=True
)

os.makedirs(
    "outputs/videos",
    exist_ok=True
)

os.makedirs(
    "outputs/logs",
    exist_ok=True
)


# ============================================================
# LOG FILE
# ============================================================

log_file = "outputs/logs/loitering_log.csv"


if not os.path.exists(log_file):

    with open(
        log_file,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Date",
            "Time",
            "Person ID",
            "Event"
        ])


# ============================================================
# VARIABLES
# ============================================================

# This timer represents when a person first occupied
# the monitored zone.

loiter_start_time = None


# ------------------------------------------------------------
# Time when the person was last successfully detected
# inside the zone.
# ------------------------------------------------------------

last_seen_in_zone = None


# ------------------------------------------------------------
# Prevents the same person/occupancy event from repeatedly
# generating alerts.
# ------------------------------------------------------------

loiter_alert_sent = False


# ------------------------------------------------------------
# Person ID used for logging/evidence.
# ------------------------------------------------------------

current_person_id = None


# ------------------------------------------------------------
# Video recording variables.
# ------------------------------------------------------------

video_writer = None

video_name = None

recording_until = None


# ------------------------------------------------------------
# Email waiting for completed video.
# ------------------------------------------------------------

pending_email = None


# ------------------------------------------------------------
# Display banner.
# ------------------------------------------------------------

show_banner = False

banner_text = ""


# ============================================================
# EMAIL FUNCTION
# ============================================================

def send_evidence_email(
    person_id,
    timestamp,
    image_path,
    video_path
):

    try:

        send_intrusion_email(
            person_id=person_id,
            timestamp=timestamp,
            image_path=image_path,
            video_path=video_path
        )

        print(
            "Owner alert email sent successfully."
        )

    except Exception as e:

        print(
            f"Email alert failed: {e}"
        )


# ============================================================
# MAIN WINDOW
# ============================================================

cv2.namedWindow(
    "AI Surveillance",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "AI Surveillance",
    1280,
    720
)


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()


    if not ret:

        print(
            "Camera stream ended."
        )

        break


    # ========================================================
    # YOLO DETECTION + TRACKING
    # ========================================================

    results = model.track(
        frame,
        persist=True,

        # ByteTrack is lighter than BoT-SORT and avoids
        # the optical-flow bottleneck seen in your traceback.
        tracker="bytetrack.yaml",

        classes=[0],

        conf=0.5,

        imgsz=416,

        verbose=False
    )


    # ========================================================
    # FRAME SETUP
    # ========================================================

    annotated_frame = frame.copy()


    # --------------------------------------------------------
    # Count people.
    # --------------------------------------------------------

    person_count = len(
        results[0].boxes
    )


    # --------------------------------------------------------
    # Current frame state.
    # --------------------------------------------------------

    person_inside_zone = False

    detected_person_id = None

    detected_person_box = None


    # ========================================================
    # PROCESS PEOPLE
    # ========================================================

    for box in results[0].boxes:


        # ----------------------------------------------------
        # Ignore detections without tracking IDs.
        # ----------------------------------------------------

        if box.id is None:
            continue


        track_id = int(
            box.id.item()
        )


        # ----------------------------------------------------
        # Bounding box.
        # ----------------------------------------------------

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0]
        )


        # ----------------------------------------------------
        # Person foot point.
        # ----------------------------------------------------

        foot_x = (
            x1 + x2
        ) // 2

        foot_y = y2


        # ====================================================
        # CHECK MONITORED AREA
        # ====================================================

        inside_zone = (
            ZONE_X1 < foot_x < ZONE_X2
            and
            ZONE_Y1 < foot_y < ZONE_Y2
        )


        # ====================================================
        # PERSON INSIDE AREA
        # ====================================================

        if inside_zone:

            person_inside_zone = True

            detected_person_id = track_id

            detected_person_box = (
                x1,
                y1,
                x2,
                y2
            )

            box_color = (
                0,
                0,
                255
            )


        else:

            box_color = (
                0,
                255,
                0
            )


        # ====================================================
        # DRAW PERSON
        # ====================================================

        cv2.rectangle(
            annotated_frame,
            (x1, y1),
            (x2, y2),
            box_color,
            2
        )


        cv2.putText(
            annotated_frame,
            f"ID {track_id}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            box_color,
            2
        )


        cv2.circle(
            annotated_frame,
            (foot_x, foot_y),
            7,
            (0, 255, 255),
            -1
        )


    # ========================================================
    # ZONE OCCUPANCY TIMER
    # ========================================================

    current_timestamp = (
        datetime.now().timestamp()
    )


    if person_inside_zone:


        # ----------------------------------------------------
        # Person detected in zone.
        # ----------------------------------------------------

        last_seen_in_zone = (
            current_timestamp
        )


        # ----------------------------------------------------
        # Start timer only once.
        # ----------------------------------------------------

        if loiter_start_time is None:

            loiter_start_time = (
                current_timestamp
            )

            current_person_id = (
                detected_person_id
            )

            print(
                "Person entered monitored zone. "
                "Loitering timer started."
            )


        # ----------------------------------------------------
        # Calculate how long the zone has been occupied.
        # ----------------------------------------------------

        loiter_duration = (
            current_timestamp
            - loiter_start_time
        )


    else:


        # ----------------------------------------------------
        # No person detected in zone.
        #
        # DO NOT immediately reset the timer.
        #
        # YOLO may miss a frame or two.
        # ----------------------------------------------------

        if (
            loiter_start_time is not None
            and
            last_seen_in_zone is not None
        ):

            missing_duration = (
                current_timestamp
                - last_seen_in_zone
            )


            if (
                missing_duration
                <= ZONE_MISSING_GRACE
            ):

                # Keep timer alive during temporary
                # detection loss.

                loiter_duration = (
                    current_timestamp
                    - loiter_start_time
                )


            else:

                # Person has actually left the area.

                print(
                    "Monitored zone is empty. "
                    "Loitering timer reset."
                )


                loiter_start_time = None

                last_seen_in_zone = None

                current_person_id = None

                loiter_alert_sent = False

                show_banner = False

                banner_text = ""

                loiter_duration = 0


        else:

            loiter_duration = 0


    # ========================================================
    # LOITERING DETECTION
    # ========================================================

    if (
        loiter_start_time is not None
        and
        loiter_duration >= LOITERING_TIME
        and
        not loiter_alert_sent
    ):


        # ----------------------------------------------------
        # Prevent duplicate alert.
        # ----------------------------------------------------

        loiter_alert_sent = True


        now = datetime.now()


        print(
            f"LOITERING DETECTED: Person "
            f"{current_person_id} has remained "
            f"for {int(loiter_duration)} seconds."
        )


        # ====================================================
        # SAVE SCREENSHOT
        # ====================================================

        image_name = (
            f"outputs/images/"
            f"loitering_{current_person_id}_"
            f"{now.strftime('%Y%m%d_%H%M%S')}.jpg"
        )


        cv2.imwrite(
            image_name,
            annotated_frame
        )


        print(
            f"Screenshot saved: {image_name}"
        )


        # ====================================================
        # SAVE LOG
        # ====================================================

        with open(
            log_file,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(file)


            writer.writerow([
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                current_person_id,
                "Loitering Detected"
            ])


        # ====================================================
        # START VIDEO RECORDING
        # ====================================================

        if video_writer is None:


            video_name = (
                f"outputs/videos/"
                f"loitering_{current_person_id}_"
                f"{now.strftime('%Y%m%d_%H%M%S')}.mp4"
            )


            fourcc = (
                cv2.VideoWriter_fourcc(
                    *"mp4v"
                )
            )


            video_writer = cv2.VideoWriter(
                video_name,
                fourcc,
                20.0,
                (1280, 720)
            )


            recording_until = (
                now.timestamp()
                + RECORDING_DURATION
            )


            pending_email = {

                "person_id":
                    current_person_id,

                "timestamp":
                    now.strftime(
                        "%d-%m-%Y %H:%M:%S"
                    ),

                "image_path":
                    image_name
            }


            print(
                f"Video recording started: "
                f"{video_name}"
            )


        # ====================================================
        # BANNER
        # ====================================================

        show_banner = True

        banner_text = (
            "LOITERING DETECTED!"
        )


    # ========================================================
    # DRAW RESTRICTED / MONITORED ZONE
    # ========================================================

    if (
        loiter_alert_sent
    ):

        zone_color = (
            0,
            0,
            255
        )

        zone_text = (
            "LOITERING DETECTED"
        )


    elif person_inside_zone:

        zone_color = (
            0,
            255,
            255
        )

        zone_text = (
            "PERSON IN MONITORED AREA"
        )


    else:

        zone_color = (
            0,
            255,
            0
        )

        zone_text = (
            "MONITORED AREA"
        )


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


    # ========================================================
    # LOITERING TIMER
    # ========================================================

    if (
        loiter_start_time is not None
    ):


        elapsed_seconds = int(
            loiter_duration
        )


        minutes = (
            elapsed_seconds // 60
        )

        seconds = (
            elapsed_seconds % 60
        )


        timer_text = (
            f"Zone Time: "
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )


        cv2.putText(
            annotated_frame,
            timer_text,
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )


        # ----------------------------------------------------
        # Remaining time.
        # ----------------------------------------------------

        remaining = max(
            0,
            LOITERING_TIME
            - elapsed_seconds
        )


        remaining_minutes = (
            remaining // 60
        )

        remaining_seconds = (
            remaining % 60
        )


        countdown_text = (
            f"Alert in: "
            f"{remaining_minutes:02d}:"
            f"{remaining_seconds:02d}"
        )


        cv2.putText(
            annotated_frame,
            countdown_text,
            (20, 195),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )


    # ========================================================
    # ALERT BANNER
    # ========================================================

    if show_banner:


        cv2.rectangle(
            annotated_frame,
            (0, 0),
            (
                annotated_frame.shape[1],
                80
            ),
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


    # ========================================================
    # PEOPLE COUNT
    # ========================================================

    cv2.putText(
        annotated_frame,
        f"People Count: {person_count}",
        (
            20,
            annotated_frame.shape[0] - 20
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )


    # ========================================================
    # CAMERA NAME
    # ========================================================

    cv2.putText(
        annotated_frame,
        "CAM-01 : CCTV FOOTAGE",
        (20, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    # ========================================================
    # DATE + TIME
    # ========================================================

    current_time = (
        datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )
    )


    cv2.putText(
        annotated_frame,
        current_time,
        (850, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # RESIZE
    # ========================================================

    annotated_frame = cv2.resize(
        annotated_frame,
        (1280, 720)
    )


    # ========================================================
    # RECORD VIDEO
    # ========================================================

    if video_writer is not None:


        video_writer.write(
            annotated_frame
        )


        if (
            datetime.now().timestamp()
            >= recording_until
        ):


            video_writer.release()

            video_writer = None


            completed_video = (
                video_name
            )


            video_name = None

            recording_until = None


            print(
                f"Video saved: "
                f"{completed_video}"
            )


            # =================================================
            # CALLING / OWNER ALERT
            # =================================================

            if pending_email is not None:


                send_evidence_email(
                    person_id=
                        pending_email["person_id"],

                    timestamp=
                        pending_email["timestamp"],

                    image_path=
                        pending_email["image_path"],

                    video_path=
                        completed_video
                )


                pending_email = None


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "AI Surveillance",
        annotated_frame
    )


    # ========================================================
    # EXIT
    # ========================================================

    key = (
        cv2.waitKey(1)
        & 0xFF
    )


    if key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

if video_writer is not None:

    video_writer.release()


    if pending_email is not None:

        send_evidence_email(
            person_id=
                pending_email["person_id"],

            timestamp=
                pending_email["timestamp"],

            image_path=
                pending_email["image_path"],

            video_path=
                video_name
        )


cap.release()

cv2.destroyAllWindows()


print(
    "CCTV surveillance system stopped."
)
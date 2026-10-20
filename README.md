# AI-Based Surveillance and Restricted-Zone Intrusion Detection System

A Python-based CCTV monitoring prototype that combines real-time person detection and tracking, restricted-zone loitering detection, camera-tampering checks, evidence capture, CSV logging, and email alerts.

## 1. Overview

The system processes an IP camera stream over RTSP and uses YOLOv8 Nano and ByteTrack to detect and track people. It monitors a predefined rectangular zone and triggers a loitering alert when a tracked person remains in the zone beyond the configured threshold of 180 seconds (3 minutes).

The prototype also includes camera-tampering checks for possible camera covering, blurring, and major view changes, along with camera connection monitoring and recovery handling.

The system is intended for testing in a controlled environment. Detection behaviour depends on camera placement, lighting, stream quality, network reliability, and hardware resources.

## 2. Features

### Person Detection and Tracking
- Uses the YOLOv8 Nano model (`yolov8n.pt`) to detect people.
- Uses ByteTrack to maintain tracking IDs across video frames.
- Monitors a person's foot point against a predefined rectangular zone.

### Restricted-Zone Loitering Detection
- Starts a timer when a tracked person enters the monitored zone.
- Uses a 180-second loitering threshold.
- Includes a short grace period for temporary detection or tracking loss.
- Captures a screenshot and approximately 10 seconds of video evidence when a loitering event is triggered.
- Records event information in CSV logs.
- Sends email alerts with evidence when configured.

### Camera-Tampering Detection

The `detection/camera_tampering.py` module analyses sampled video frames for possible tampering events:

- **Camera covered:** Based on a significant drop in image brightness.
- **Camera blurred:** Based on a drop in image sharpness.
- **Major view change:** Based on changes in the grayscale histogram.

The detector establishes a baseline during startup and uses a confirmation duration and cooldown to reduce repeated alerts. These image-based heuristics may produce false positives when lighting or the scene changes significantly.

### Camera Connection Monitoring
- Detects camera stream disconnection.
- Supports reconnection and recovery handling in the main surveillance workflow.
- Sends offline and recovery status alerts when configured.

### Evidence, Logging, and Alerts
- Uses the Resend API for email notifications.
- Supports screenshot and video evidence attachments for applicable alerts.
- Stores event information in CSV logs.
- Stores generated output files under `outputs/`, which is excluded from Git.

## 3. Technology Stack

- Python 3.11
- OpenCV
- Ultralytics YOLOv8 Nano
- ByteTrack
- RTSP and IP CCTV camera
- Resend API
- `python-dotenv`
- CSV logging

## 4. System Architecture

The main surveillance workflow follows this process:

```text
IP Camera
    |
    | RTSP Stream
    v
OpenCV Video Capture
    |
    v
YOLOv8 Person Detection
    |
    v
ByteTrack Person Tracking
    |
    v
Monitored-Zone Check
    |
    v
Loitering Timer
    |
    | Person remains beyond 180 seconds
    v
Loitering Event
    |
    +-------------------+
    |                   |
    v                   v
Screenshot         Video Evidence
    |                   |
    +---------+---------+
              |
              v
         CSV Logging
              |
              v
         Email Alert
```

Camera-tampering checks and camera connection monitoring operate as additional parts of the surveillance workflow.

## 5. Repository Structure

```text
AI-Surveillance-System/
├── detection/
│   ├── __init__.py
│   └── camera_tampering.py
├── src/
│   └── alerts.py
├── main_video.py
├── main_webcam.py
├── yolov8n.pt
├── requirements.txt
├── .gitignore
└── README.md
```

This is the documented core project structure. Your local checkout may contain additional diagnostic scripts. Generated evidence, virtual environments, and local configuration files should not be committed.

## 6. Requirements

- Python 3.11
- An IP camera with an RTSP stream for the CCTV workflow
- A computer capable of running OpenCV and the YOLO model
- A Resend account and API key if email notifications are required

The webcam entry point can be used for testing if it is supported by your current setup.

## 7. Installation

Open PowerShell in the project directory.

### Step 1: Create a Virtual Environment

```powershell
python -m venv venv
```

### Step 2: Activate the Environment

```powershell
.\venv\Scripts\Activate.ps1
```

If you already have a working virtual environment, activate it instead of creating another one.

### Step 3: Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 8. Configuration

Create a local `.env` file in the project root if your implementation reads these values from environment variables.

Example:

```dotenv
CAMERA_PASSWORD=replace_with_your_camera_password
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxx
ALERT_EMAIL=you@example.com
```

Use the exact environment variable names expected by the current code.

Configure the camera's RTSP address according to the camera model and stream settings. Keep camera credentials and credential-bearing RTSP URLs out of the README and source control.

**Never commit your real `.env` file, camera password, API key, or private email configuration.**

## 9. Running the Project

### CCTV Surveillance

From the repository root, run:

```powershell
python main_video.py
```

The program attempts to connect to the configured camera stream and start the surveillance workflow. Ensure the camera is reachable and the local configuration is correct.

### Webcam Testing

If the webcam entry point matches your intended test setup, run:

```powershell
python main_webcam.py
```

## 10. Detection Workflow

The loitering detection process follows these steps:

1. Read a frame from the video stream.
2. Detect people using YOLOv8.
3. Track detections using ByteTrack.
4. Determine each tracked person's foot point.
5. Check whether the foot point lies inside the configured zone.
6. Start and maintain the zone-presence timer.
7. Trigger a loitering event after the 180-second threshold is exceeded.
8. Capture a screenshot and approximately 10 seconds of video evidence.
9. Record event information in the CSV log.
10. Send an email alert with evidence when configured.

A short detection or tracking grace period helps prevent temporary detection loss from immediately resetting the timer.

The camera-tampering detector separately compares sampled frames against a startup baseline using brightness, sharpness, and grayscale histogram information. Confirmation durations and cooldowns help limit repeated alerts.

## 11. Evidence and Logs

Generated files are stored under `outputs/` when the application runs. Depending on the implementation and event type, this may include:

| Location | Purpose |
|---|---|
| `outputs/images/` | Captured screenshots |
| `outputs/videos/` | Recorded video evidence |
| `outputs/logs/` | CSV event logs |

The loitering log can record event information such as date, time, person ID, and event type, depending on the current implementation.

The `outputs/` directory is excluded from Git to avoid publishing private CCTV footage and generated evidence. Review local files before sharing them.

## 12. Testing

Test the system in a controlled environment and verify each behaviour separately.

- Person detection and tracking
- Entry into and exit from the monitored zone
- Loitering threshold and evidence capture
- Email delivery and attachment handling
- Camera-covered detection
- Camera-blurred detection
- Major-view-change detection
- Camera stream disconnection and recovery

The project documentation does not claim measured detection accuracy, frames per second (FPS), or alert latency. Add performance metrics only after measuring them under defined test conditions.

## 13. Current Limitations

- The monitored zone is predefined and rectangular.
- The current detection workflow focuses on people.
- Camera-tampering detection uses image-based heuristics and may flag legitimate lighting or scene changes.
- The system depends on camera-stream availability and network reliability.
- Performance depends on available CPU/GPU resources.
- The prototype uses pretrained YOLOv8 Nano weights rather than a custom-trained model.
- The current implementation is designed around a single monitored camera.

## 14. Future Enhancements

Possible improvements include:

- Multiple-camera support and configurable monitoring zones
- A web-based monitoring dashboard
- Database-backed event storage
- Additional notification channels, such as WhatsApp
- Cloud-based evidence storage
- Automatic camera discovery
- Custom model training for specific surveillance environments
- Improved anomaly and tampering detection
- User authentication and access control
- Measured performance and reliability benchmarks

These are proposed enhancements, not claims about features already implemented.

## 15. Security and Privacy

- Never commit `.env` files, camera passwords, API keys, or credential-bearing RTSP URLs.
- Do not publish private CCTV recordings, screenshots, or logs containing personal information.
- Use camera accounts with appropriate permissions.
- Rotate any credentials or API keys that may have been exposed.
- Avoid disabling TLS certificate verification in code used outside controlled local testing.
- Obtain appropriate authorization before monitoring a location and follow applicable privacy requirements.

## 16. Acknowledgement

This project explores the application of computer vision, object tracking, and automated notifications to restricted-zone monitoring and CCTV event awareness.
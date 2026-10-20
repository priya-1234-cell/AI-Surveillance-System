AI-Based Surveillance and Restricted-Zone Intrusion Detection System
A Python-based CCTV monitoring prototype that combines real-time person detection, tracking, restricted-zone loitering detection, camera-tampering checks, evidence capture, CSV logging, and email alerts.
Overview
The system processes an IP camera stream over RTSP and uses YOLOv8 and ByteTrack to detect and track people. It monitors a predefined rectangular zone and raises a loitering alert when a tracked person remains there for more than 180 seconds (3 minutes).

The project also includes camera-tampering checks for covered, blurred, or major-view-change conditions, along with camera connection status monitoring. Events can generate email alerts and supporting evidence.
This is a prototype intended for testing in a controlled environment. Detection behaviour depends on camera placement, lighting, stream quality, and hardware.

Features
Person detection and tracking
- Uses the YOLOv8 Nano model (yolov8n.pt) to detect people.
- Uses ByteTrack to maintain tracking IDs between frames.
- Monitors the person's foot point against a configured rectangular zone.
Restricted-zone loitering detection
- Starts a timer when a tracked person enters the monitored zone.
- Uses a 180-second loitering threshold.
- Includes a short grace period for temporary detection or tracking loss.
- Captures a screenshot and approximately 10 seconds of video evidence when a loitering event is triggered.
- Records event information in CSV logs and sends an email alert with evidence.
Camera-tampering detection
The detection/camera_tampering.py module analyses sampled frames for possible:
- CAMERA COVERED events, based on a large drop in brightness.
- CAMERA BLURRED events, based on a drop in image sharpness.
- MAJOR VIEW CHANGE events, based on a change in the grayscale histogram.
The detector establishes a baseline during startup and uses a confirmation duration and cooldown to reduce repeated alerts. These image-based heuristics can produce false positives when lighting or the scene changes significantly.
Camera connection monitoring
- Detects camera stream disconnection.
- Supports recovery/reconnection handling in the main surveillance workflow.
- Sends status alerts for offline and recovered states when configured.
Alerts, evidence, and logs
- Uses the Resend API for email notifications.
- Can attach event screenshots and video evidence to supported alerts.
- Stores event logs as CSV files.
- Keeps generated output files under outputs/, which is excluded from Git by .gitignore.
Technology stack
- Python 3.11
- OpenCV
- Ultralytics YOLOv8 Nano
- ByteTrack
- RTSP / IP CCTV camera
- Resend API
- python-dotenv
- CSV logging
Repository structure
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
The exact files in your local checkout may include additional diagnostic scripts. Generated output, virtual environments, and local configuration should not be committed.
Requirements
- Python 3.11
- An IP camera with an RTSP stream, or another supported video source for the relevant entry point
- A computer capable of running OpenCV and the YOLO model
- A Resend account/API key if email alerts are to be used
Install the Python dependencies from the project root:
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
If you already have a virtual environment, activate that environment instead of creating another one.
Configuration
Create a local .env file in the project root if your implementation reads configuration through environment variables. Use placeholders in documentation and never commit the real .env file.

Example:
CAMERA_PASSWORD=replace_with_your_camera_password
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxx
ALERT_EMAIL=you@example.com
Use the variable names expected by the current code. Keep camera credentials, API keys, private email addresses, and other secrets out of source files and Git history.

Configure the camera's RTSP address in the appropriate local configuration/code according to your camera model and stream settings. Do not publish a credential-bearing RTSP URL.
Run the surveillance system
From PowerShell in the repository root:
python main_video.py
The program attempts to connect to the configured camera stream and starts the surveillance workflow. Ensure the camera is reachable and that the local configuration is correct.

A webcam entry point is also present in the repository:
python main_webcam.py
Use the webcam entry point only if it matches your intended test setup.
Detection workflow
1. Read a frame from the video stream.
2. Run YOLOv8 person detection.
3. Track detections using ByteTrack.
4. Check the tracked person's foot point against the configured zone.
5. Start and maintain the zone-presence timer.
6. Trigger a loitering event after the 180-second threshold.
7. Capture a screenshot and approximately 10 seconds of video.
8. Write event information to CSV and send the configured email alert.
The camera-tampering detector separately compares frame brightness, sharpness, and histogram information against a startup baseline. Candidate events must persist for the configured confirmation period, and cooldowns help limit repeated alerts.
Evidence and logs
Generated files are written under outputs/ when the application runs. Depending on the event and current configuration, this can include:
- outputs/images/ for screenshots
- outputs/videos/ for recorded evidence
- outputs/logs/ for CSV event logs
The outputs/ directory is ignored by Git to avoid publishing private CCTV footage and generated artifacts. Review evidence locally and share it only when appropriate.
Security and privacy notes
- Never commit .env, camera passwords, API keys, or credential-bearing RTSP URLs.
- Do not publish private CCTV recordings, screenshots, or logs containing personal information.
- Use camera accounts with appropriate permissions and change any credentials that may have been exposed.
- Avoid disabling TLS certificate verification in code used outside a controlled local test.
- Obtain appropriate authorization before monitoring a location and follow applicable privacy requirements.
Testing notes
Test the system in a controlled setup and verify each behaviour separately:
- Person detection and tracking
- Entry into and exit from the monitored zone
- Loitering threshold and evidence capture
- Email delivery and attachment handling
- Camera covered, blurred, and major-view-change scenarios
- Camera stream disconnection and recovery
The project documentation does not claim a measured detection accuracy, FPS, or latency benchmark. Results depend on the environment and hardware, so performance metrics should only be added after measuring them.
Current limitations
- The monitored zone is predefined and rectangular.
- The current detection workflow focuses on people.
- Camera-tampering detection uses image heuristics and may flag legitimate lighting or scene changes.
- The system depends on camera-stream availability and network reliability.
- Performance depends on available CPU/GPU resources.
- The prototype uses pretrained YOLOv8 Nano weights rather than a custom-trained model.
- The current implementation is designed around a single monitored camera.
Future enhancements
- Multiple cameras and configurable zones
- Web-based monitoring dashboard
- Database-backed event storage
- Additional notification channels
- Improved tampering detection and calibration
- Authentication and access control
- Measured performance and reliability benchmarks
Acknowledgement
This project explores the application of computer vision and automated notifications to restricted-zone monitoring and CCTV event awareness.
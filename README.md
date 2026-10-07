\# AI-Based Surveillance and Loitering Detection System

\## 1. Project Overview
The AI-Based Surveillance and Loitering Detection System is a real-time CCTV monitoring system designed to detect when a person remains inside a predefined monitored zone for longer than a specified duration.
The system uses an IP camera as the video source and applies computer vision to detect and track people. If a person remains inside the monitored zone for more than 3 minutes, the system generates an alert and stores visual evidence.
The alert mechanism currently uses email. The email contains the captured screenshot and recorded video as evidence of the detected event.
\---
\## 2. Objectives
The main objectives of the system are:
\- Monitor a designated area using an IP camera.
\- Detect people in the camera feed using YOLO.
\- Track detected people across video frames.
\- Define a monitored zone within the camera view.
\- Measure how long a person remains inside the zone.
\- Detect loitering when the person remains for more than 3 minutes.
\- Capture a screenshot when loitering is detected.
\- Record video evidence of the event.
\- Send an email alert to the owner with the evidence attached.
\- Maintain a log of detected loitering events.
\---
\## 3. System Features
\### Real-Time Person Detection
The system uses the YOLO object detection model to detect people in the live camera stream.
Only the `person` class is monitored.
\### Person Tracking
ByteTrack is used to maintain tracking identities across consecutive video frames.
Each detected person is assigned a tracking ID.
\### Monitored Zone
A rectangular zone is defined within the camera frame.
The system determines whether a detected person's foot point is inside this zone.
\### Loitering Detection
A timer starts when a person enters the monitored zone.
The current threshold is:
```text
180 seconds (3 minutes)
If the person remains in the zone beyond this threshold, a loitering event is triggered.
Evidence Capture
When a loitering event is detected:
\- A screenshot is captured.
\- A 10-second video recording is generated.
\- The event is recorded in a CSV log.
Email Alert
After the evidence recording is completed, an email is sent to the configured alert address.
The email contains:
\- Camera information
\- Person tracking ID
\- Date and time
\- Loitering event information
\- Screenshot evidence
\- Video evidence
4\. System Architecture
IP Camera
&#x20;   |
&#x20;   | RTSP Stream
&#x20;   v
OpenCV Video Capture
&#x20;   |
&#x20;   v
YOLO Person Detection
&#x20;   |
&#x20;   v
ByteTrack Person Tracking
&#x20;   |
&#x20;   v
Monitored Zone Check
&#x20;   |
&#x20;   v
Loitering Timer
&#x20;   |
&#x20;   | > 3 Minutes
&#x20;   v
Loitering Event
&#x20;   |
&#x20;   +-------------------+
&#x20;   |                   |
&#x20;   v                   v
Screenshot          Video Recording
&#x20;   |                   |
&#x20;   +---------+---------+
&#x20;             |
&#x20;             v
&#x20;       Email Alert
&#x20;             |
&#x20;             v
&#x20;       Owner / User
5\. Technologies Used
\- Python
\- OpenCV
\- Ultralytics YOLO
\- YOLOv8 Nano (yolov8n.pt)
\- ByteTrack
\- RTSP
\- CP Plus IP Camera
\- Resend API
\- python-dotenv
\- CSV
6\. Hardware Requirements
The system can operate with:
\- IP CCTV camera
\- Wi-Fi router or Ethernet connection
\- Laptop/Desktop computer
The prototype was designed to work with a CP Plus IP camera providing an RTSP stream.
7\. Software Requirements
\- Python 3.11
\- OpenCV
\- Ultralytics
\- PyTorch
\- Resend
\- python-dotenv
All required Python packages are listed in:
requirements.txt
8\. Project Structure
AI-Surveillance-Sytem/
│
├── main\_video.py
├── yolov8n.pt
├── requirements.txt
├── .gitignore
├── README.md
│
├── src/
│   └── alerts.py
│
├── outputs/
│   ├── images/
│   ├── videos/
│   └── logs/
│
└── venv/
File Description
File / Folder	Purpose
main\_video.py	Main surveillance and loitering detection program
yolov8n.pt	YOLOv8 Nano pretrained model
requirements.txt	Python dependencies
.gitignore	Prevents sensitive and unnecessary files from being committed
README.md	Project documentation
src/alerts.py	Email alert functionality
outputs/images/	Stores event screenshots
outputs/videos/	Stores recorded evidence
outputs/logs/	Stores event logs
venv/	Python virtual environment
9\. Configuration
Sensitive configuration values are stored in a .env file.
Example:
CAMERA\_PASSWORD=your\_camera\_password
RESEND\_API\_KEY=your\_resend\_api\_key
ALERT\_EMAIL=your\_email@example.com
The .env file must not be committed to GitHub.
10\. Camera Configuration
The system connects to the IP camera using an RTSP stream.
The RTSP stream follows the camera's supported format:
rtsp://<username>:<password>@<camera-ip>:554/video/live?channel=1\&subtype=1
The prototype uses the camera's lower-resolution substream for more efficient processing.
The camera video encoding is configured to H.264.
11\. Running the Project
Step 1: Activate the Virtual Environment
On Windows PowerShell:
.\\venv\\Scripts\\Activate.ps1
Step 2: Install Dependencies
pip install -r requirements.txt
Step 3: Configure Environment Variables
Create a .env file in the project root:
CAMERA\_PASSWORD=your\_camera\_password
RESEND\_API\_KEY=your\_resend\_api\_key
ALERT\_EMAIL=your\_email@example.com
Step 4: Run the Surveillance System
python main\_video.py
The program connects to the camera and starts real-time surveillance.
12\. Loitering Detection Logic
The system follows the following process:
1\. Capture a frame from the IP camera.
2\. Detect people using YOLO.
3\. Track detected people using ByteTrack.
4\. Determine the person's foot point.
5\. Check whether the foot point lies inside the monitored zone.
6\. Start a timer when a person enters the zone.
7\. Continue tracking the person's presence.
8\. If the person remains for at least 180 seconds, trigger a loitering event.
9\. Capture a screenshot.
10\. Record approximately 10 seconds of video.
11\. Store the event information in the CSV log.
12\. Send an email containing the evidence.
A short detection or tracking grace period is used so that temporary detection loss does not immediately reset the loitering timer.
13\. Output
Generated evidence is stored under:
outputs/
Images
outputs/images/
Contains screenshots captured when a loitering event is detected.
Videos
outputs/videos/
Contains recorded video evidence of detected events.
Logs
outputs/logs/loitering\_log.csv
The log records:
\- Date
\- Time
\- Person ID
\- Event
14\. Alert Workflow
Person detected
&#x20;     |
&#x20;     v
Person enters monitored zone
&#x20;     |
&#x20;     v
Timer starts
&#x20;     |
&#x20;     v
Person remains for 3 minutes
&#x20;     |
&#x20;     v
Loitering detected
&#x20;     |
&#x20;     +----> Screenshot
&#x20;     |
&#x20;     +----> 10-second video
&#x20;     |
&#x20;     +----> CSV log
&#x20;     |
&#x20;     v
Evidence recording completed
&#x20;     |
&#x20;     v
Email sent to owner
15\. Testing
The system was tested under multiple conditions.
Test 1: Person enters the monitored zone
Expected result:
Loitering timer starts.
Test 2: Person leaves before 3 minutes
Expected result:
No loitering alert.
Test 3: Person remains for more than 3 minutes
Expected result:
Loitering alert triggered.
Screenshot captured.
Video recorded.
Email sent.
Event logged.
Test 4: Temporary detection or tracking loss
Expected result:
Timer should not immediately reset.
A short grace period is used to handle temporary detection loss.
16\. Current Limitations
\- The system currently monitors a predefined rectangular zone.
\- The system currently detects people only.
\- Email is the implemented alert mechanism.
\- The system depends on a stable RTSP camera connection.
\- Performance depends on the available CPU/GPU resources.
\- The current prototype uses a pretrained YOLOv8 Nano model and does not involve custom model training.
\- The system is designed for a single monitored camera in the current implementation.
17\. Future Enhancements
Possible future improvements include:
\- WhatsApp alert integration.
\- Multiple camera support.
\- Multiple monitored zones.
\- Improved tracking robustness.
\- Automatic camera discovery.
\- Web-based monitoring dashboard.
\- Database-based event storage.
\- Cloud-based evidence storage.
\- Custom model training for specific surveillance environments.
\- More advanced anomaly detection.
\- User authentication and access control.
18\. Conclusion
The AI-Based Surveillance and Loitering Detection System provides an automated approach to monitoring a restricted area using an IP camera and computer vision.
The system combines real-time person detection, object tracking, zone monitoring, time-based loitering detection, evidence recording, event logging, and email notification into a single surveillance workflow.
The implemented prototype successfully detects prolonged presence inside the monitored zone and provides the owner with visual evidence through automated email alerts.

import os
import html
import resend
from dotenv import load_dotenv

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")


def _attachments_for_paths(*paths):
    """Build Resend attachments only for files that exist."""
    attachments = []
    for path in paths:
        if path and os.path.isfile(path):
            with open(path, "rb") as file:
                attachments.append({
                    "filename": os.path.basename(path),
                    "content": list(file.read()),
                })
    return attachments


def _send_email(subject, heading, details, attachment_paths=()):
    """Send a security event email. Raises on configuration/API errors."""
    recipient = os.getenv("ALERT_EMAIL")
    if not resend.api_key:
        raise RuntimeError("RESEND_API_KEY is not configured in .env")
    if not recipient:
        raise RuntimeError("ALERT_EMAIL is not configured in .env")

    rows = "".join(
        f"<p><b>{html.escape(str(label))}:</b> {html.escape(str(value))}</p>"
        for label, value in details
    )
    email_data = {
        "from": os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev"),
        "to": [recipient],
        "subject": subject,
        "html": f"<h2>{html.escape(heading)}</h2>{rows}",
    }
    attachments = _attachments_for_paths(*attachment_paths)
    if attachments:
        email_data["attachments"] = attachments
    response = resend.Emails.send(email_data)
    print(f"Security alert email submitted: {subject}")
    return response


def send_intrusion_email(person_id, timestamp, image_path=None, video_path=None):
    """Send loitering alert with available screenshot/video evidence."""
    return _send_email(
        subject="Loitering Alert - CAM-01",
        heading="Loitering Detected",
        details=[
            ("Camera", "CAM-01 : MAIN ENTRANCE"),
            ("Person ID", person_id),
            ("Date & Time", timestamp),
            ("Event", "A person remained in the monitored zone for more than 3 minutes."),
            ("Evidence", "Screenshot and video are attached when available."),
        ],
        attachment_paths=(image_path, video_path),
    )


def send_tampering_email(event, timestamp, image_path=None):
    """Send confirmed camera-tampering event with screenshot if available."""
    return _send_email(
        subject=f"Camera Tampering Alert - CAM-01: {event}",
        heading="Camera Tampering Detected",
        details=[
            ("Camera", "CAM-01 : MAIN ENTRANCE"),
            ("Date & Time", timestamp),
            ("Event", event),
            ("Evidence", "A camera snapshot is attached when available."),
        ],
        attachment_paths=(image_path,),
    )


def send_camera_status_email(event, timestamp):
    """Send camera offline/recovered status notification."""
    return _send_email(
        subject=f"CCTV Status Alert - CAM-01: {event}",
        heading="CCTV Connection Status",
        details=[
            ("Camera", "CAM-01 : MAIN ENTRANCE"),
            ("Date & Time", timestamp),
            ("Event", event),
        ],
    )

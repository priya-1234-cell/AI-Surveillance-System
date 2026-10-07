import os
import resend
from dotenv import load_dotenv


load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


def send_intrusion_email(
    person_id,
    timestamp,
    image_path=None,
    video_path=None
):

    attachments = []


    # ========================================================
    # SCREENSHOT ATTACHMENT
    # ========================================================

    if image_path and os.path.exists(image_path):

        with open(image_path, "rb") as file:

            attachments.append({
                "filename": os.path.basename(image_path),
                "content": list(file.read())
            })


    # ========================================================
    # VIDEO ATTACHMENT
    # ========================================================

    if video_path and os.path.exists(video_path):

        with open(video_path, "rb") as file:

            attachments.append({
                "filename": os.path.basename(video_path),
                "content": list(file.read())
            })


    # ========================================================
    # EMAIL
    # ========================================================

    email_data = {

        "from": "onboarding@resend.dev",

        "to": [
            os.getenv("ALERT_EMAIL")
        ],

        "subject": "Loitering Alert - CAM-01",

        "html": f"""
            <h2>Loitering Detected</h2>

            <p>
                <b>Camera:</b>
                CAM-01 : MAIN ENTRANCE
            </p>

            <p>
                <b>Person ID:</b>
                {person_id}
            </p>

            <p>
                <b>Date & Time:</b>
                {timestamp}
            </p>

            <p>
                <b>Event:</b>
                A person remained in the monitored zone
                for more than 3 minutes.
            </p>

            <p>
                Screenshot and video evidence are attached
                to this email.
            </p>
        """
    }


    # ========================================================
    # ADD ATTACHMENTS
    # ========================================================

    if attachments:

        email_data["attachments"] = attachments


    # ========================================================
    # SEND EMAIL
    # ========================================================

    response = resend.Emails.send(
        email_data
    )


    print(
        "Owner alert email sent successfully."
    )


    return response
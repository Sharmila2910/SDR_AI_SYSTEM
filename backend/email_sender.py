from fastapi import APIRouter, Form, HTTPException
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

router = APIRouter()

@router.post("/send-email/")
async def send_email(
    prospect_email: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
):
    """Send the reviewed email to the prospect."""
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "nsharmila2910@gmail.com"  # My email
        smtp_password = "hsft nhgd qjkv oalm"      # app password

        msg = MIMEMultipart()
        msg['From'] = formataddr(("Sharmila", smtp_username))
        msg['To'] = prospect_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        return {"status": "Email sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email: str, otp: str):
    if not settings.smtp_email or not settings.smtp_password:
        logger.warning("SMTP credentials not configured. OTP: %s (NOT SENT to %s)", otp, email)
        return False

    msg = MIMEMultipart()
    msg['From'] = settings.smtp_email
    msg['To'] = email
    msg['Subject'] = "Your OTP Code"

    body = f"Your OTP is {otp} (valid for 5 minutes)"
    msg.attach(MIMEText(body, 'plain'))

    try:
        logger.info("Connecting to SMTP server %s:%s...", settings.smtp_host, settings.smtp_port)
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10)
        server.set_debuglevel(1)  # Enable debug output for logs
        server.starttls()
        server.login(settings.smtp_email, settings.smtp_password)
        text = msg.as_string()
        server.sendmail(settings.smtp_email, email, text)
        server.quit()
        logger.info("Successfully sent OTP email to %s", email)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", email, str(e))
        return False

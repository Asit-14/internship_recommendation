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
        import socket
        try:
            resolved_ip = socket.gethostbyname(settings.smtp_host)
            logger.info("Resolved %s to %s", settings.smtp_host, resolved_ip)
        except Exception as dns_err:
            logger.error("DNS Resolution failed for %s: %s", settings.smtp_host, str(dns_err))

        logger.info("Connecting to SMTP server %s:%s...", settings.smtp_host, settings.smtp_port)
        
        if settings.smtp_port == 465:
            # Use SMTP_SSL for port 465
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15)
        else:
            # Use STARTTLS for other ports (like 587)
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15)
            server.starttls()
            
        server.set_debuglevel(1)
        server.login(settings.smtp_email, settings.smtp_password)
        text = msg.as_string()
        server.sendmail(settings.smtp_email, email, text)
        server.quit()
        logger.info("Successfully sent OTP email to %s", email)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", email, str(e))
        # Log specific details if it's a network issue
        if "Network is unreachable" in str(e):
            logger.error("Network issue detected. Try changing SMTP_PORT to 465 or check if your hosting provider blocks outbound SMTP.")
        return False

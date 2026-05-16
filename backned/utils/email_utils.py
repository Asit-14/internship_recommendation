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

    msg = MIMEMultipart("alternative")  # upgraded to support HTML
    msg['From'] = settings.smtp_email
    msg['To'] = email
    msg['Subject'] = "Your OTP Code"

    # -------- Existing Plain Text (UNCHANGED) --------
    body = f"Your OTP is {otp} (valid for 5 minutes)"
    msg.attach(MIMEText(body, 'plain'))

    # -------- ADVANCED HTML BOILERPLATE --------
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>OTP Verification</title>
    </head>
    <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, sans-serif;">
        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="padding:20px;">
            <tr>
                <td>
                    <table align="center" width="500" cellpadding="0" cellspacing="0"
                        style="background:#ffffff; border-radius:10px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                        
                        <!-- Header -->
                        <tr>
                            <td style="text-align:center; padding-bottom:20px;">
                                <h2 style="margin:0; color:#333;">🔐 OTP Verification</h2>
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="color:#555; font-size:14px;">
                                <p>Hello,</p>
                                <p>Your One-Time Password (OTP) is:</p>

                                <div style="text-align:center; margin:25px 0;">
                                    <span style="
                                        display:inline-block;
                                        padding:12px 25px;
                                        font-size:26px;
                                        letter-spacing:3px;
                                        font-weight:bold;
                                        color:#ffffff;
                                        background:#2d89ef;
                                        border-radius:6px;">
                                        {otp}
                                    </span>
                                </div>

                                <p>This OTP is valid for <strong>5 minutes</strong>.</p>
                                <p>If you did not request this, please ignore this email.</p>
                            </td>
                        </tr>

                        <!-- Divider -->
                        <tr>
                            <td>
                                <hr style="border:none; border-top:1px solid #eee; margin:20px 0;">
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="font-size:12px; color:#999; text-align:center;">
                                <p>This is an automated email. Please do not reply.</p>
                                <p>&copy; 2026 Your Company. All rights reserved.</p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

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
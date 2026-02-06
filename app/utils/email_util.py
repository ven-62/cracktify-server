import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config

def send_email(receiver_email, subject, message):
    SENDER_EMAIL = Config.EMAIL_SENDER
    APP_PASSWORD = Config.EMAIL_PASSWORD

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "html"))

    try:
        # Set timeout to 10 seconds
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)

        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()

        return {"success": True, "message": "Email sent successfully"}

    except smtplib.SMTPException as e:
        return {"success": False, "message": f"SMTP error: {str(e)}"}

    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {str(e)}"}

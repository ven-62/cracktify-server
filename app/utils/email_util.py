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
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)

        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()

        print("Email sent successfully!")

    except Exception as e:
        print("Error sending email:", e)

if __name__ == "__main__":
    send_email("venlavapie62@gmail.com", "Test Email from FastAPI", "<h1>This is a test email sent from FastAPI!</h1><p>It works!</p>")
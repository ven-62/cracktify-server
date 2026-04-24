import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.config import Config

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    creds = Credentials.from_authorized_user_info(Config.TOKEN_INFO, SCOPES)
    return build("gmail", "v1", credentials=creds)


def send_email(receiver_email: str, subject: str, html_content: str):
    service = get_gmail_service()

    message = MIMEText(html_content, "html")
    message["to"] = receiver_email
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(userId="me", body={"raw": raw}).execute()

    return {"success": True, "message": "Email sent successfully"}

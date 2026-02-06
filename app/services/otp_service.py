import asyncio
from datetime import datetime, timezone, timedelta
from app.models.otp import OTP
from app.models.user import User
from app.utils.otp import generate_otp, verify_otp
from app.utils.email_util import send_email
from app.templates.otp_template import otp_email_template, forgot_password_otp_template

OTP_EXPIRATION_MINUTES = 5

def send_email_otp(email_address: str, name: str, resend: bool, db):
    now = datetime.now(timezone.utc)

    if resend:
        db.query(OTP).filter(OTP.email_address == email_address).delete()
        db.commit()

    # Remove existing valid OTP
    db.query(OTP).filter(
        OTP.email_address == email_address,
        OTP.expires_at > now
    ).delete()
    db.commit()

    otp_code = generate_otp()

    # Save OTP FIRST
    new_otp = OTP(
        email_address=email_address,
        otp=otp_code,
        created_at=now,
        expires_at=now + timedelta(minutes=OTP_EXPIRATION_MINUTES)
    )
    db.add(new_otp)
    db.commit()

    # Send email via Gmail API
    subject = "Your One-Time PIN (OTP)"
    content = otp_email_template(name, otp_code)

    response = send_email(email_address, subject, content)

    if not response.get("success"):
        return {
            "success": False,
            "message": response.get("message", "Failed to send OTP email")
        }

    return {"success": True, "message": "OTP has been sent to your email"}


def send_forgot_password_otp(email_address: str, db):
    user = db.query(User).filter(User.email_address == email_address).first()
    if not user:
        return {"success": False, "message": "Email not found"}

    otp = generate_otp()

    new_otp = OTP(
        email_address=email_address,
        otp=otp,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRATION_MINUTES)
    )
    db.add(new_otp)
    db.commit()

    subject = "Your Password Reset OTP"
    content = forgot_password_otp_template(user.first_name, otp)

    response = send_email(email_address, subject, content)

    if not response.get("success"):
        return {
            "success": False,
            "message": "OTP saved but email delivery failed"
        }

    return {"success": True, "message": "OTP has been sent to your email"}

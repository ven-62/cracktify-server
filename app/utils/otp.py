import random
from datetime import datetime, timezone

def generate_otp():
    return str(
        [random.randint(0, 9) for _ in range(6)]).replace("[", "").replace("]", "").replace(",", "").replace(" ", "")

def verify_otp(last_otp, entered_otp, datenow):
    if not last_otp:
        return False

    # Ensure expires_at is timezone-aware
    expires_at = last_otp.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datenow > expires_at:
        return False

    return last_otp.otp == entered_otp


if __name__ == "__main__":
    otp = generate_otp()
    print(f"Generated OTP: {otp}")

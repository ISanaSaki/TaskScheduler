import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

async def send_email(to: str, subject: str, body: str):
    message = MIMEMultipart()
    message["From"] = f"{settings.SMTP_FROM} <{settings.SMTP_USER}>"
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from email import encoders
import pytest
import smtplib

load_dotenv()

GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
RECIPENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
audio_file_path = 'test_data/podcast_7a501041ef974e0c95a54c38005a4801.mp3'  # Replace with your actual audio file path
def test_send_email_with_attachment():
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = RECIPENT_EMAIL
    msg['Subject'] = 'Your Podcast Audio File'
    # Attach the audio file
    with open(audio_file_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(audio_file_path)}')
        msg.attach(part)

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        print(f"Email sent to {RECIPENT_EMAIL} with attachment {audio_file_path}")

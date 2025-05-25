import os
import imaplib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')

def test_gmail_imap_connection():
    try:
        # Connect to Gmail's IMAP server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        print("Gmail IMAP connection successful.")
        mail.logout()
    except imaplib.IMAP4.error as e:
        print("Failed to connect to Gmail IMAP:", e)

# Run the test
test_gmail_imap_connection()

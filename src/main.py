import os
from dotenv import load_dotenv
from gmail_handler import connect_to_gmail, fetch_newsletter_content
from podcastfy.client import generate_podcast
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def main():
    
    mail = connect_to_gmail(GMAIL_USER, GMAIL_PASSWORD)
    
    # Select inbox
    mail.select('inbox')
    
    # Search for specific emails (e.g., TLDR newsletters)
    status, messages = mail.search(None, 'FROM "dan@tldrnewsletter.com"')
    
    if messages[0]:
        email_ids = messages[0].split()
        
        # Load existing newsletter data if file exists
        import json
        import os
        
        newsletters_file = 'data/formatted_email_output/newsletters.json'
        newsletters_data = []
        
        if os.path.exists(newsletters_file):
            try:
                with open(newsletters_file, 'r') as f:
                    newsletters_data = json.load(f)
                print(f"Loaded {len(newsletters_data)} existing newsletters from {newsletters_file}")
            except (json.JSONDecodeError, FileNotFoundError):
                print("Starting with empty newsletter collection")
        
        # Get existing message IDs to avoid duplicates
        existing_message_ids = {newsletter.get('message_id') for newsletter in newsletters_data if newsletter.get('message_id')}
        
        # Process all emails
        processed_count = 0
        for email_id in email_ids:
            try:
                result, email_data = fetch_newsletter_content(mail, email_id)
                
                # Skip if we already have this email
                if email_data.get('message_id') in existing_message_ids:
                    continue
                
                # Create simplified newsletter entry
                newsletter_entry = {
                    'message_id': email_data.get('message_id'),
                    'subject': email_data.get('subject'),
                    'from': email_data.get('from'),
                    'date': email_data.get('date'),
                    'cleaned_content': email_data.get('content_only', ''),
                    'newsletter_sections': [
                        {
                            'title': section.get('title', ''),
                            'content': section.get('content', '')
                        }
                        for section in email_data.get('newsletter_sections', [])
                    ],
                    'newsletter_articles': [
                        {
                            'title': article.get('title', ''),
                            'content': article.get('content', ''),
                            'read_time': article.get('read_time', '')
                        }
                        for article in email_data.get('newsletter_articles', [])
                    ]
                }
                
                newsletters_data.append(newsletter_entry)
                processed_count += 1
                
                print(f"Processed: {email_data.get('subject', 'Unknown Subject')}")
                
            except Exception as e:
                print(f"Error processing email {email_id}: {str(e)}")
                continue
        
        # Save updated newsletter data
        if processed_count > 0:
            with open(newsletters_file, 'w') as f:
                json.dump(newsletters_data, f, indent=4)
            print(f"\nProcessed {processed_count} new newsletters")
            print(f"Total newsletters saved: {len(newsletters_data)}")
            print(f"Data saved to {newsletters_file}")
        else:
            print("No new newsletters to process")
        
        # Display latest newsletter info
        if newsletters_data:
            latest = newsletters_data[-1]
            print(f"\nLatest Newsletter:")
            print(f"Subject: {latest['subject']}")
            print(f"From: {latest['from']}")
            print(f"Date: {latest['date']}")
            print(f"Sections: {len(latest['newsletter_sections'])}")
            print(f"Articles: {len(latest['newsletter_articles'])}")
    
    mail.close()
    mail.logout()
    return newsletters_data

def send_email_with_attachment(audio_file_path, recipient_email):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = recipient_email
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
        print(f"Email sent to {recipient_email} with attachment {audio_file_path}")
        



if __name__ == "__main__":
    content = main()
    audio_file = generate_podcast(text = content[0]["cleaned_content"], tts_model="openai", llm_model_name="gpt-4-turbo",api_key_label = "openai_api_key")  # Specify models)
    
    # Send the audio file via email
    send_email_with_attachment(audio_file, 'cederquist94@hotmail.com')

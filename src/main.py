import os
import json
import smtplib
from dotenv import load_dotenv
from gmail_handler import connect_to_gmail, fetch_newsletter_content
from podcastfy.client import generate_podcast
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def load_environment_variables():
    load_dotenv()
    return {
        'GMAIL_USER': os.getenv('GMAIL_USER'),
        'GMAIL_PASSWORD': os.getenv('GMAIL_PASSWORD'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY')
    }

def connect_to_mail(gmail_user, gmail_password):
    mail = connect_to_gmail(gmail_user, gmail_password)
    mail.select('inbox')
    return mail

def load_newsletters_data(newsletters_file):
    newsletters_data = []
    if os.path.exists(newsletters_file):
        try:
            with open(newsletters_file, 'r') as f:
                newsletters_data = json.load(f)
            print(f"Loaded {len(newsletters_data)} existing newsletters from {newsletters_file}")
        except (json.JSONDecodeError, FileNotFoundError):
            print("Starting with empty newsletter collection")
    return newsletters_data

def process_emails(mail, email_ids, existing_message_ids):
    newsletters_data = []
    processed_count = 0
    for email_id in email_ids:
        try:
            result, email_data = fetch_newsletter_content(mail, email_id)
            if email_data.get('message_id') in existing_message_ids:
                continue
            
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
    return newsletters_data, processed_count

def save_newsletters_data(newsletters_data, newsletters_file):
    with open(newsletters_file, 'w') as f:
        json.dump(newsletters_data, f, indent=4)
    print(f"Data saved to {newsletters_file}")

def display_latest_newsletter(newsletters_data):
    if newsletters_data:
        latest = newsletters_data[-1]
        print(f"\nLatest Newsletter:")
        print(f"Subject: {latest['subject']}")
        print(f"From: {latest['from']}")
        print(f"Date: {latest['date']}")
        print(f"Sections: {len(latest['newsletter_sections'])}")
        print(f"Articles: {len(latest['newsletter_articles'])}")

def send_email_with_attachment(audio_file_path, recipient_email, gmail_user, gmail_password):
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = recipient_email
    msg['Subject'] = 'Your Podcast Audio File'

    with open(audio_file_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(audio_file_path)}')
        msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        print(f"Email sent to {recipient_email} with attachment {audio_file_path}")

def generate_audio(content):
    return generate_podcast(text=content[0]["cleaned_content"], tts_model="openai", llm_model_name=llm_model, api_key_label=api_key_label)

def main():
    global email_contact, llm_model, api_key_label
    email_contact = 'cederquist94@hotmail.com'
    llm_model = 'gpt-4-turbo'
    api_key_label = 'openai_api_key'
    env_vars = load_environment_variables()
    mail = connect_to_mail(env_vars['GMAIL_USER'], env_vars['GMAIL_PASSWORD'])
    
    status, messages = mail.search(None, 'FROM "dan@tldrnewsletter.com"')
    
    newsletters_file = 'data/formatted_email_output/newsletters.json'
    newsletters_data = load_newsletters_data(newsletters_file)
    
    existing_message_ids = {newsletter.get('message_id') for newsletter in newsletters_data if newsletter.get('message_id')}
    
    newsletters_data, processed_count = process_emails(mail, messages[0].split(), existing_message_ids)
    
    if processed_count > 0:
        save_newsletters_data(newsletters_data, newsletters_file)
        print(f"\nProcessed {processed_count} new newsletters")
        print(f"Total newsletters saved: {len(newsletters_data)}")
    else:
        print("No new newsletters to process")
    
    display_latest_newsletter(newsletters_data)
    
    mail.close()
    mail.logout()
    return newsletters_data

if __name__ == "__main__":
    content = main()
    audio_file = generate_audio(content)
    send_email_with_attachment(audio_file, 'cederquist94@hotmail.com', os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASSWORD'))

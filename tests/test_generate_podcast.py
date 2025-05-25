# test_generate_podcast.py

from gmail_handler import connect_to_gmail, search_newsletters, fetch_newsletter_content, extract_plain_text
from src.newsletter_parser import NewsletterParser
from podcastfy.client import generate_podcast

def test_generate_podcast():
    # Step 1: Connect to Gmail and fetch newsletters
    mail = connect_to_gmail()
    newsletter_ids = search_newsletters(mail)
    
    # Step 2: Extract text from the fetched newsletters
    all_text = ""
    parser = NewsletterParser()
    emails = []

    for email_id in newsletter_ids:
        content = fetch_newsletter_content(mail, email_id)
        emails.append({
            'body': content,
            'subject': 'Subject Placeholder',  # Placeholder, as we don't have the subject here
            'sender': 'dan@tldrnewsletter.com',  # Placeholder for sender
            'date': 0,  # Placeholder for date
            'unread': True  # Placeholder for unread status
        })

    parsed_contents = parser.parse_newsletters(emails)
    print("Parsed contents:", parsed_contents)  # Debugging line
    assert False
    
    
    all_text = "\n".join(parsed_contents)  # Combine all parsed contents
    breakpoint()  # Debugging point to inspect all_text

    # Step 3: Generate audio from the extracted text
    audio_file = generate_podcast(text=all_text, tts_model="openai", llm_model_name="gpt-4-turbo", api_key_label="openai_api_key")

    if audio_file:
        print("Audio generated successfully:", audio_file)
    else:
        print("Failed to generate audio.")

if __name__ == "__main__":
    test_generate_podcast()

import email
import imaplib
import re
import unicodedata

def clean_email_text(raw_text):
    """Clean up messy email text content."""
    if not raw_text:
        return ""
    
    text = raw_text
    
    # Step 1: Handle common escape sequences
    text = text.replace('\\r\\n', '\n')
    text = text.replace('\\n', '\n')
    text = text.replace('\\r', '\n')
    
    # Step 2: Remove/replace problematic Unicode characters
    # Non-breaking spaces
    text = text.replace('\xa0', ' ')
    # Zero-width characters (often used in emails to prevent parsing)
    text = text.replace('\u200c', '')  # Zero-width non-joiner
    text = text.replace('\u200b', '')  # Zero-width space
    text = text.replace('\u200d', '')  # Zero-width joiner
    text = text.replace('\ufeff', '')  # Byte order mark
    
    # Step 3: Normalize Unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # Step 4: Clean up excessive whitespace
    # Replace multiple consecutive spaces with single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Replace multiple consecutive newlines with double newline (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Step 5: Remove trailing/leading whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Step 6: Remove empty lines at start and end
    text = text.strip()
    
    return text

def remove_email_metadata(text):
    """Remove common email metadata and navigation elements."""
    # Remove common email header/footer patterns
    patterns_to_remove = [
        r'Sign Up \[\d+\].*?View Online \[\d+\]',
        r'Links:\s*------.*?$',  # Remove links section at end
        r'Manage your subscriptions.*?unsubscribe.*?\.',
        r'Want to advertise.*?ADVERTISE WITH US.*?\.',
        r'If you have any comments.*?just respond to this email!',
        r'\[SPONSOR\]',
        r'TOGETHER WITH.*?\]',
        r'Want to work at TLDR\?.*?get \$1k if we hire them!',
        r'Thanks for reading,.*?(?=\n\n|\Z)',  # Remove signature section
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    return text.strip()

def extract_newsletter_sections(text):
    """Extract and structure newsletter content into sections."""
    sections = []
    current_section = {'title': '', 'content': ''}
    
    for line in text.split('\n'):
        if not line:
            continue
            
        # Detect section headers (all caps, short lines, common section names)
        if (line.isupper() and len(line) < 100 and 
            any(keyword in line for keyword in [
                'DEEP DIVES', 'OPINIONS', 'ADVICE', 'LAUNCHES', 'TOOLS', 
                'QUICK LINKS', 'MISCELLANEOUS', 'SPONSORS'
            ])):
            
            if current_section['content'].strip():
                sections.append(current_section.copy())
            current_section = {'title': line.strip(), 'content': ''}
            
        else:
            current_section['content'] += line + '\n'
    
    # Add the last section
    if current_section['content'].strip():
        sections.append(current_section)
    
    return sections

def extract_newsletter_articles(text):
    """Extract individual articles from newsletter content."""
    articles = []
    
    # Pattern to match article titles (usually in ALL CAPS followed by read time)
    article_pattern = r'^([A-Z][A-Z\s&:,\'-]+?)(\s*\([\d\w\s]+\))?\s*(\[\d+\])?$'
    
    lines = text.split('\n')
    current_article = {'title': '', 'content': '', 'read_time': '', 'link_id': ''}
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if this looks like an article title
        match = re.match(article_pattern, line)
        if match and len(line) > 20:  # Avoid short headers
            # Save previous article if it exists
            if current_article['title'] and current_article['content'].strip():
                articles.append(current_article.copy())
            
            # Start new article
            title = match.group(1).strip()
            read_time = match.group(2).strip('() ') if match.group(2) else ''
            link_id = match.group(3).strip('[] ') if match.group(3) else ''
            
            current_article = {
                'title': title,
                'content': '',
                'read_time': read_time,
                'link_id': link_id
            }
        else:
            # Add to current article content
            current_article['content'] += line + '\n'
    
    # Add the last article
    if current_article['title'] and current_article['content'].strip():
        articles.append(current_article)
    
    return articles

def process_newsletter(raw_email_text):
    """Complete newsletter processing pipeline."""
    
    # Step 1: Basic cleaning
    cleaned = clean_email_text(raw_email_text)
    
    # Step 2: Remove metadata
    content_only = remove_email_metadata(cleaned)
    
    # Step 3: Extract structured content
    sections = extract_newsletter_sections(content_only)
    
    # Step 4: Extract individual articles
    articles = extract_newsletter_articles(content_only)
    
    return {
        'cleaned_text': cleaned,
        'content_only': content_only,
        'sections': sections,
        'articles': articles
    }

def fetch_newsletter_content(mail, email_id):
    """Fetch and parse the content of the email by ID."""
    result, data = mail.fetch(email_id, '(RFC822)')
    raw_email = data[0][1]
    
    # Parse the raw email into a structured format
    msg = email.message_from_bytes(raw_email)
    
    # Extract structured data
    email_data = {
        'from': msg['From'],
        'to': msg['To'],
        'subject': msg['Subject'],
        'date': msg['Date'],
        'message_id': msg['Message-ID'],
        'body_text': '',
        'body_html': '',
        'attachments': []
    }
    
    # Handle multipart emails
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Skip multipart containers
            if content_type == "multipart/alternative" or content_type == "multipart/mixed":
                continue
                
            # Extract text content
            if content_type == "text/plain" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True)
                if body:
                    email_data['body_text'] = body.decode('utf-8', errors='ignore')
                    
            elif content_type == "text/html" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True)
                if body:
                    email_data['body_html'] = body.decode('utf-8', errors='ignore')
                    
            # Handle attachments
            elif part.get_filename():
                email_data['attachments'].append({
                    'filename': part.get_filename(),
                    'content_type': content_type,
                    'size': len(part.get_payload(decode=True)) if part.get_payload(decode=True) else 0
                })
    else:
        # Single part email
        content_type = msg.get_content_type()
        body = msg.get_payload(decode=True)
        if body:
            if content_type == "text/html":
                email_data['body_html'] = body.decode('utf-8', errors='ignore')
            else:
                email_data['body_text'] = body.decode('utf-8', errors='ignore')
    
    # Clean and process the extracted text content
    if email_data['body_text']:
        newsletter_processed = process_newsletter(email_data['body_text'])
        email_data['body_text_cleaned'] = newsletter_processed['cleaned_text']
        email_data['content_only'] = newsletter_processed['content_only']
        email_data['newsletter_sections'] = newsletter_processed['sections']
        email_data['newsletter_articles'] = newsletter_processed['articles']
    
    return result, email_data

def connect_to_gmail(gmail_user, gmail_password):
    """Connect to Gmail IMAP server."""
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(gmail_user, gmail_password)
    return mail
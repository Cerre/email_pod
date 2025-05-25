# newsletter_parser.py

import re
from datetime import datetime, timedelta
from typing import List, Optional
from bs4 import BeautifulSoup

class NewsletterParser:
    def __init__(self, emails: List[dict] = []):
        self.emails = emails

    def _filter_recent_newsletters(self) -> List[dict]:
        """Filter emails to get only unread newsletters from the last 24 hours."""
        recent_newsletters = []
        cutoff_time = datetime.now() - timedelta(days=1)

        for email in self.emails:
            email_time = datetime.fromtimestamp(email['date'])
            if email['unread'] and email_time > cutoff_time:
                recent_newsletters.append(email)

        return recent_newsletters

    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract plain text from HTML email content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove unwanted elements like ads or unsubscribe links
        for unwanted in soup.find_all(['script', 'style', 'a']):
            unwanted.decompose()
        return soup.get_text(separator="\n").strip()

    def parse_newsletters(self) -> dict:
        """Parse the newsletters to extract structured content."""
        newsletters_dict = {}

        recent_newsletters = self.emails  # Assuming we are processing all emails for now

        for email in recent_newsletters:
            text_content = self._extract_text_from_html(email['body'])
            breakpoint()

            newsletter_title = email['subject']  # Use the email subject as the newsletter title
            
            if newsletter_title not in newsletters_dict:
                newsletters_dict[newsletter_title] = {}

            for section in sections:
                # Further split each section to get news titles and text
                lines = section.strip().split("\n")
                if len(lines) > 1:
                    news_title = lines[0]  # First line as news title
                    news_text = "\n".join(lines[1:])  # Remaining lines as news text
                    newsletters_dict[newsletter_title][news_title] = news_text

        return newsletters_dict

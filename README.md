# Daily Newsletter to Podcast System

A Python system that automatically converts daily newsletters (specifically TLDR AI) into podcast-style audio summaries using Podcastfy and delivers them via email.

## Overview

This system:
1. Fetches daily TLDR AI newsletters from your Gmail inbox
2. Extracts and processes the newsletter content
3. Generates a conversational podcast using Podcastfy
4. Emails the MP3 file back to you
5. Runs automatically every day at 7 AM (Stockholm time)

## Features

- **Gmail Integration**: Connects securely to Gmail via IMAP/SMTP
- **Smart Content Processing**: Extracts key sections from TLDR newsletters
- **AI-Powered Podcast Generation**: Uses Podcastfy for conversational audio
- **Automated Scheduling**: Runs daily via cron job
- **Error Handling**: Robust error recovery and logging
- **Self-Hosted**: Runs entirely on your own Linux server

## Quick Start

### Prerequisites

- Python 3.11+
- Linux system (Ubuntu/Debian recommended)
- Gmail account with TLDR AI newsletter subscription
- API key for OpenAI or Google Gemini

### Installation

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd daily-podcast
   python -m venv daily-podcast-env
   source daily-podcast-env/bin/activate
   ```

2. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install ffmpeg  # For audio processing
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (see Configuration section)
   ```

### Configuration

Edit the `.env` file with your credentials:

```bash
# Gmail credentials
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-app-password  # Generate from Gmail security settings

# API keys (choose one)
OPENAI_API_KEY=your-openai-key
# OR
GEMINI_API_KEY=your-gemini-key

# Optional: Email recipient (defaults to same as GMAIL_USER)
RECIPIENT_EMAIL=your-email@gmail.com
```

#### Gmail Setup

1. **Enable 2-Step Verification** (if not already enabled)
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in GMAIL_PASSWORD

### Testing

Test individual components:

```bash
# Test Gmail connection
python -m src.gmail_handler

# Test Podcastfy integration
python -m src.podcast_generator

# Test full system
python src/main.py
```

### Scheduling

Set up daily execution at 7 AM Stockholm time:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path to your installation)
0 7 * * * cd /path/to/daily-podcast && /path/to/daily-podcast-env/bin/python src/main.py >> logs/cron.log 2>&1
```

## Project Structure

```
daily-podcast/
├── README.md               # This file
├── TASKS.MD               # Implementation tasks
├── SYSTEM.MD              # Development framework
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore file
├── src/
│   ├── __init__.py
│   ├── gmail_handler.py   # Gmail IMAP/SMTP operations
│   ├── content_processor.py # Newsletter text processing
│   ├── podcast_generator.py # Podcastfy integration
│   └── main.py           # Main execution script
├── tests/                 # Unit tests
├── config/               # Configuration files
├── logs/                 # Application logs
└── output/              # Temporary podcast files
```

## How It Works

1. **Newsletter Detection**: Searches Gmail for unread TLDR AI newsletters from the last 24 hours
2. **Content Extraction**: Parses the email HTML and extracts clean text content
3. **Content Processing**: Removes ads/links and formats content for podcast generation
4. **Podcast Generation**: Uses Podcastfy to create conversational audio from the newsletter content
5. **Delivery**: Emails the generated MP3 file to your specified address
6. **Cleanup**: Removes temporary files and logs completion

## Troubleshooting

### Common Issues

**Gmail Authentication Errors**:
- Ensure 2-Step Verification is enabled
- Use App Password, not regular password
- Check that IMAP is enabled in Gmail settings

**No Newsletter Found**:
- Verify you're subscribed to TLDR AI newsletter
- Check that newsletters aren't going to spam
- Confirm the newsletter sender format hasn't changed

**Podcastfy Errors**:
- Verify your API key is correct and has sufficient credits
- Check that the newsletter content isn't too long
- Review logs for specific error messages

**Audio Quality Issues**:
- Adjust voice settings in `config/podcast_config.json`
- Try different TTS models in Podcastfy configuration

### Logs

Check logs for debugging:
```bash
# Application logs
tail -f logs/daily-podcast.log

# Cron job logs
tail -f logs/cron.log
```

### Manual Execution

Test the system manually:
```bash
# Run with debug logging
python src/main.py --debug

# Process specific date
python src/main.py --date 2025-05-21
```

## Development

See `TASKS.MD` for detailed implementation tasks and `SYSTEM.MD` for development framework.

To run tests:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the patterns in `SYSTEM.MD`
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Open an issue with log output and system details
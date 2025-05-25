from podcastfy.client import generate_podcast

def test_text_to_speech():
    # Sample newsletter text
    sample_text = "Here is an example text that discusses AI news."
    
    # Generate audio from the sample text
    audio_file = generate_podcast(urls=["https://www.anthropic.com/news/claude-4"], tts_model="openai", llm_model_name="gpt-4-turbo",api_key_label = "openai_api_key")  # Specify models
    
    if audio_file:
        print("Audio generated successfully:", audio_file)
    else:
        print("Failed to generate audio.")

# Run the test
if __name__ == "__main__":
    test_text_to_speech()

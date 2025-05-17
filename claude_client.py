import os
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Anthropic client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

def ask_claude(prompt, model="claude-3-7-sonnet-20250219", max_tokens=1000):
    """
    Send a prompt to Claude and get a response
    """
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Example usage
    prompt = "What are three key concepts in agentic AI?"
    response = ask_claude(prompt)
    print(response)
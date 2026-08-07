import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_tags(text: str):

    prompt = f"""
Generate 3 to 5 short tags for this incident.

Rules:
- Return only comma separated tags.
- No numbering.
- No explanation.
- Tags should be lowercase.

Incident:
{text}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=30
        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        print("=" * 50)
        print("Groq Error:")
        print(repr(e))
        print("=" * 50)

        return "general"
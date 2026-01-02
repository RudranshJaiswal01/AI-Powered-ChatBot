import os
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def summarize_chunk(chunk_text: str) -> str:
    prompt = f"""
Summarize the following text in 1–3 concise sentences.
Do not add extra information.

Text:
{chunk_text}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        top_p=1,
        max_tokens=3072,
        stream=False,
        stop=None
    )
    return response.choices[0].message.content.strip()
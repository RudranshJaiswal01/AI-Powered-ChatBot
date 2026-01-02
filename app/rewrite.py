import os
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

MAX_HISTORY = 5


def rewrite_query(query: str, history: list[str]) -> str:
    """
    Rewrites follow-up queries into standalone questions.
    Uses history ONLY for rewriting.
    """

    if not history:
        return query

    history = history[-MAX_HISTORY:]
    formatted_history = "\n".join(history)

    prompt = f"""
Rewrite the user's question to be standalone and clear.

Conversation history:
{formatted_history}

Current question:
{query}

Standalone rewritten question:
"""


    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        top_p=1,
        max_tokens=1024,
        stream=False,
        stop=None
    )
    rewritten = response.choices[0].message.content.strip()
    return rewritten.strip('"').strip("'")


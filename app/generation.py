import os
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are an AI assistant answering questions strictly using the provided document excerpts.

Rules:
- Use ONLY the provided document excerpts.
- After every factual statement, append the citation EXACTLY as provided (copy-paste).
- Do NOT invent citation formats (no numbers, no line references).
- Do NOT summarize citations.
- If multiple excerpts support a statement, list multiple citations.
- If the answer is not explicitly present, reply with exactly:
"This information is not present in the document."
"""

def generate_answer(question: str, evidence: list[dict]) -> str:
    if not evidence:
        return "This information is not present in the document."

    excerpts = "\n\n".join(
        f"[SOURCE]\n{e['text']}\n[CITATION]\n{e['citation']}"
        for e in evidence
    )


    user_prompt = f"""
Question:
{question}

Document excerpts:
{excerpts}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_completion_tokens=8192,
        top_p=1,
        reasoning_effort="medium",
        stream=False,
        stop=None
    )

    return response.choices[0].message.content.strip()

def generate_document_summary(chunk_summaries: list[dict]) -> str:
    ordered = sorted(
        chunk_summaries,
        key=lambda x: (str(x["section"]), x["page"])
    )

    joined = "\n".join(
        f"- {c['summary']} (Section {c['section']}, Page {c['page']})"
        for c in ordered
    )

    prompt = f"""
You are given summaries of all sections of a document.

Create a concise, well-structured overall summary.
Do NOT invent information.

Content:
{joined}
"""

    return generate_answer(prompt, [])

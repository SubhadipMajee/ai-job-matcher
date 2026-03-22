import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_skills(text, source="resume"):
    prompt = f"""
Extract a list of technical skills from the following {source} text.
Return ONLY a Python list of strings, nothing else.
Example: ["Python", "React", "SQL"]

Text:
{text}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    try:
        skills = eval(raw)
        return skills
    except:
        return []
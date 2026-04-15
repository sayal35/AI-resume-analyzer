from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# for m in client.models.list():
#     print(m.name)

MODELS = [    
    "gemini-2.0-flash",           
    "gemini-2.5-flash",                      
    "gemini-flash-latest",       
    "gemini-pro-latest"           
]

def analyze_resume(resume_text, user_goal):

    prompt = f"""
SYSTEM RULE:
You are a strict JSON-only response engine.

IMPORTANT OUTPUT RULES:
- You must follow instructions exactly
- Return ONLY valid JSON
- No explanations
- No markdown
- No extra text before or after JSON

================ USER TASK ================

You are a senior software engineer and hiring engineer.

Evaluate the resume based on user's goal.

User goal: "{user_goal}"

STRICT RULES:
- Extract only relevant skills for this goal
- Remove irrelevant tools
- Identify real gaps
- Generate roadmap only for missing fields
- Make output DIFFERENT based on goal

IMPORTANT:
You MUST always include "career_prospects" as a list of strings.

Return ONLY valid JSON:
{{

  "skills": [],
  "missing_skills": [],
  "roadmap": [],
  "interview_questions": [],
  "career_prospects": []
}}

Resume:
{resume_text}

===========================================
"""
    for model in MODELS:
        try:
            response = client.models.generate_content(
            model=model,
            contents=prompt
        )

            content = response.text.strip()

            # remove possible markdown noise
            content = content.replace("```json", "").replace("```", "")

            # safe JSON extraction
            start = content.find("{")
            end = content.rfind("}") + 1

            return json.loads(content[start:end])

        except Exception as e:
            return {
                "skills": [],
                "missing_skills": [],
                "roadmap": [],
                "interview_questions": [],
                "career_prospects": [],
                "error": str(e)
            }
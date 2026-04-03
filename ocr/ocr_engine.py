import io
import base64
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4.1"


def extract_text(image):
    """
    Extract student name and subject marks from a marksheet image using OpenAI Vision.
    Returns: (name: str, subjects: dict)
    """
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()

        prompt = """
You are an expert OCR + structured academic marksheet extraction AI.

Extract:

1) Student Full Name
2) Subject-wise final marks obtained

Rules:
- Ignore roll number, seat number, board name.
- Ignore total percentage.
- Extract only final marks.
- Marks must be integers.
- If name unclear, return "User".

Return STRICT JSON:

{
  "name": "Full Name Here",
  "subjects": {
    "Subject1": 85,
    "Subject2": 91
  }
}

Return only JSON.
"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        name = data.get("name", "User")
        subjects = data.get("subjects", {})

        clean_subjects = {}
        for subject, mark in subjects.items():
            try:
                mark = int(mark)
                if 0 <= mark <= 100:
                    clean_subjects[subject.strip()] = mark
            except:
                continue

        return name, clean_subjects

    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return "User", {}
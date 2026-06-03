import asyncio
from os import getenv

from google import genai
from pydantic import BaseModel
from PIL import Image
import os


class PressureData(BaseModel):
    sys: int
    dia: int
    pul: int

# Твой клиент
client = genai.Client(api_key=getenv("API_KEY"))


async def get_pressure_from_gemini(image_path):
    if not os.path.exists(image_path):
        return {"error": "File not found"}

    try:
        image = Image.open(image_path)

        model_id = "gemini-2.5-flash"

        prompt = (
            "Extract blood pressure readings from this 7-segment display. "
            "Top is Systolic, middle is Diastolic, bottom is Pulse."
        )

        response = client.models.generate_content(
            model=model_id,
            contents=[image, prompt],
            config={
                'response_mime_type': 'application/json',
                'response_schema': PressureData,
            }
        )

        return response.parsed.model_dump()

    except Exception as e:
        return {"error": "API_ERROR", "msg": str(e)}

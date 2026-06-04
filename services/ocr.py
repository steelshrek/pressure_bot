import os
from os import getenv

from dotenv import load_dotenv
from google import genai
from PIL import Image
from pydantic import BaseModel

load_dotenv()


class PressureData(BaseModel):
    sys: int
    dia: int
    pul: int


api_key = getenv("API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


async def get_pressure_from_gemini(image_path):
    if not os.path.exists(image_path):
        return {"error": "FILE_NOT_FOUND", "msg": "Файл не знайдено."}

    if client is None:
        return {"error": "API_KEY_MISSING", "msg": "Не налаштовано API_KEY у файлі .env."}

    try:
        image = Image.open(image_path)
        prompt = (
            "Extract blood pressure readings from this 7-segment display. "
            "Top is Systolic, middle is Diastolic, bottom is Pulse."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, prompt],
            config={
                "response_mime_type": "application/json",
                "response_schema": PressureData,
            }
        )

        return response.parsed.model_dump()
    except Exception as exc:
        return {"error": "API_ERROR", "msg": str(exc)}

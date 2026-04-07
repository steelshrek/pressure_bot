import os
from os import getenv
from google import genai
from pydantic import BaseModel
from PIL import Image

# Описываем структуру данных
class PressureData(BaseModel):
    sys: int
    dia: int
    pul: int

# Твой клиент (убедись, что API_KEY в переменной окружения)
client = genai.Client(api_key=getenv("API_KEY"))

async def get_pressure_from_gemini(image_path):
    if not os.path.exists(image_path):
        return {"error": "File not found"}

    try:
        # Важно: для google-genai лучше передавать Image напрямую вот так:
        image = Image.open(image_path)
        model_id = "gemini-2.0-flash" # 2.5 не существует, юзай 2.0
        prompt = (
            "Extract blood pressure readings from the image. "
            "The large number labeled 'SYS' is systolic pressure. "
            "The large number labeled 'DIA' is diastolic pressure. "
            "The number next to 'PUL' (usually at the bottom) is the pulse. "
            "Ignore date and time. Return as JSON with keys: sys, dia, pul."
        )
        response = client.models.generate_content(
            model=model_id,
            contents=[image, prompt],
            config={
                'response_mime_type': 'application/json',
                'response_schema': PressureData,
            }
        )

        if response.parsed:
            return response.parsed.model_dump()
        return {"error": "empty_parsed"}

    except Exception as e:
        print(f"!!! GEMINI CRASH: {e}") # Увидишь в логах Render
        return {"error": str(e)}
import os
from os import getenv
from google import genai
from pydantic import BaseModel
from PIL import Image
from typing import Any


class PressureData(BaseModel):
    # Используем Any, чтобы валидация не падала, если придет строка вместо числа
    sys: Any
    dia: Any
    pul: Any


client = genai.Client(api_key=getenv("API_KEY"))


async def get_pressure_from_gemini(image_path):
    if not os.path.exists(image_path):
        return {"error": "File not found"}

    try:
        image = Image.open(image_path)
        model_id = "gemini-2.0-flash"

        prompt = (
            "Extract systolic, diastolic pressure and pulse from this medical monitor. "
            "Return JSON with keys 'sys', 'dia', 'pul'. Use ONLY numbers. "
            "If a value is not found, use 0."
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
            data = response.parsed.model_dump()
            # Пытаемся принудительно превратить в инты, если пришли строки
            return {
                "sys": int(data.get("sys", 0)),
                "dia": int(data.get("dia", 0)),
                "pul": int(data.get("pul", 0))
            }

        return {"error": "empty_parsed"}

    except Exception as e:
        # ОБЯЗАТЕЛЬНО: это покажет в логах Render, почему именно упало
        print(f"!!! GEMINI ERROR: {e}")
        return {"error": str(e)}
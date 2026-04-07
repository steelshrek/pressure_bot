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
client = genai.Client(api_key=getenv("GEMINI_API_KEY"))

async def get_pressure_from_gemini(image_path):
    if not os.path.exists(image_path):
        return {"error": "File not found"}

    try:
        # Открываем изображение
        image = Image.open(image_path)

        # Ставим актуальную модель (2.0 или 1.5)
        model_id = "gemini-2.0-flash"

        prompt = (
            "Extract blood pressure readings from this 7-segment display. "
            "Top is Systolic (sys), middle is Diastolic (dia), bottom is Pulse (pul)."
        )

        # Выполняем запрос
        response = client.models.generate_content(
            model=model_id,
            contents=[image, prompt],
            config={
                'response_mime_type': 'application/json',
                'response_schema': PressureData,
            }
        )

        # Проверяем, удалось ли распарсить данные
        if response.parsed:
            return response.parsed.model_dump()
        else:
            return {"error": "PARSING_ERROR", "msg": "Gemini couldn't parse the image"}

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"error": "API_ERROR", "msg": str(e)}
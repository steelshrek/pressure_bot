import asyncio
from os import getenv

from google import genai
from pydantic import BaseModel  # Обычно идет вместе с библиотекой
from PIL import Image
import os


# Описываем структуру данных, которую хотим получить
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

        # Используем 2.5-flash, раз она у тебя в списке первая
        model_id = "gemini-2.5-flash"

        prompt = (
            "Extract blood pressure readings from this 7-segment display. "
            "Top is Systolic, middle is Diastolic, bottom is Pulse."
        )

        # Используем response_mime_type для получения чистого JSON
        response = client.models.generate_content(
            model=model_id,
            contents=[image, prompt],
            config={
                'response_mime_type': 'application/json',
                'response_schema': PressureData,
            }
        )

        # Теперь response.parsed — это уже готовый объект/словарь
        return response.parsed.model_dump()

    except Exception as e:
        return {"error": "API_ERROR", "msg": str(e)}


# if __name__ == "__main__":
#     photo = 'LD-51Ssmall.jpg'
#     print(f"--- Анализ фото через {photo} ---")
#
#     result = asyncio.run(get_pressure_from_gemini(photo))
#
#     if "error" not in result:
#         print(f"Результат: {result}")
#         print(f"\nДанные распознаны: {result['sys']}/{result['dia']}, Пульс: {result['pul']}")
#     else:
#         print(f"Ошибка: {result}")
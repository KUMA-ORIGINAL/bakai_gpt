import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.assistant import Assistant

STATIC_DIR = "/static/photos"

async def load_fixtures(session: AsyncSession, fixture_path: str = "fixtures/assistants.json"):
    with open(fixture_path, "r", encoding="utf-8") as file:
        assistants_data = json.load(file)

    for assistant_data in assistants_data:
        result = await session.execute(
            select(Assistant).where(Assistant.name == assistant_data["name"])
        )
        if not result.scalar_one_or_none():
            # Формируем правильный путь к файлу
            assistant_data["photo"] = f"{STATIC_DIR}/{assistant_data['photo']}"
            assistant = Assistant(**assistant_data)
            session.add(assistant)

    await session.commit()

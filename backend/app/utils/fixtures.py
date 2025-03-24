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


Маркетолог-Мээрим	Поможет с продвижением бизнеса	11	/static/photos/Marketer - Meerim.webp
 edit	Юрист-Айбек	Консультации по договорам, спорам и правовым вопросам	12	/static/photos/Aibek yurist.webp
 edit	Бухгалтер-Айсулуу	Поможет с учетом, отчетностью и налогами компании	13	/static/photos/buhgalter aisuluu.webp
 edit	Финансист-Тахир	Поможет планировать бюджет, инвестиции и расходы	14	/static/photos/finansist tahir.webp
 edit	Эксперт по автоматизации-Мирель	Оптимизирует бизнес-процессы и внедрит автоматизацию	15	/static/photos/avtom Mirel.webp
import asyncio

from openai import AsyncOpenAI
from typing import AsyncGenerator

from config import settings
from models import Assistant, Chat
from services.chat_service import ChatService

api_key = settings.openai.api_key

client = AsyncOpenAI(api_key=api_key)

bakai_assistant_id = settings.openai.bakai_assistant_id


async def get_assistant_response(
        user_message: str, chat: Chat, assistant: Assistant, chat_service: ChatService
) -> AsyncGenerator[str, None]:
    if assistant.name == "Math Tutor":
        assistant_id = bakai_assistant_id

    try:
        if assistant_id:
            assistant = await client.beta.assistants.retrieve(assistant_id)
            if not chat.thread_id:
                thread = await client.beta.threads.create()
                thread_id = thread.id
                await chat_service.update_chat(chat.id, thread_id=thread_id)
            else:
                thread_id = chat.thread_id
            await client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )
            async with client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=assistant.id,
            ) as stream:
                async for event in stream:  # Итерируем через поток событий
                    if event.event == "thread.message.delta":
                        yield event.data.delta.content[0].text.value  # Отправляем текст сразу,
                await asyncio.sleep(0.5)  # Проверяем статус выполнения каждые 1 сек

    except Exception as e:
        print(f"Ошибка при запросе к OpenAI API: {e}")
        yield "Извините, произошла ошибка."

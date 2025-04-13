import asyncio
import logging

from openai import AsyncOpenAI
from typing import AsyncGenerator

from config import settings
from models import Assistant, Chat
from services.chat_service import ChatService

api_key = settings.openai.api_key

client = AsyncOpenAI(api_key=api_key)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_assistant_id(assistant: Assistant):
    assistants_id = {
        'Эксперт по автоматизации-Мирель': settings.openai.bakai_automate_id,
        'Финансист-Тахир': settings.openai.bakai_finance_id,
        'Юрист-Айбек': settings.openai.bakai_legal_id,
        'Маркетолог-Мээрим': settings.openai.bakai_marketer_id,
        'Бухгалтер-Айсулуу': settings.openai.bakai_accountant_id
    }
    return assistants_id[assistant.name]


async def get_assistant_response(
    user_message: str,
    chat: Chat,
    assistant: Assistant,
    chat_service: ChatService,
    file_ids: list = None,  # [{file_id, filename}]
    b64_images: list = None  # [{file_id, filename}]
) -> AsyncGenerator[str, None]:

    assistant = await client.beta.assistants.create(
        name="Читающий Документы",
        instructions="Ты помощник, отвечающий на основе приложенных файлов.",
        model="gpt-4-1106-preview",
        tools=[{"type": "code_interpreter"}]
    )

    # assistant_id = get_assistant_id(assistant)
    assistant_id = assistant.id

    try:
        if not chat.thread_id:
            thread = await client.beta.threads.create()
            thread_id = thread.id
            await chat_service.update_chat(chat.id, thread_id=thread_id)
        else:
            thread_id = chat.thread_id

        attachments = []
        if file_ids:
            for file_id in file_ids:
                attachments.append({
                    "file_id": file_id,
                    "tools": [{"type": "code_interpreter"}]
                })

        # content = []
        #
        # if user_message:
        #     content.append({"type": "text", "text": user_message})

        # if b64_images:
        #     for b64_data in b64_images:
        #         if b64_data:
        #             content.append({
        #                 "type": "image_url",
        #                 "image_url": {"url": f"data:image/png;base64,{b64_data}"}
        #             })

        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message,
            attachments=attachments or None,
        )

        async with client.beta.threads.runs.stream(thread_id=thread_id, assistant_id=assistant_id) as stream:
            async for event in stream:
                logger.info(f"Stream event: {event.event} → {event.data}")
                if event.event == "thread.message.delta":
                    delta = event.data.delta
                    if delta and delta.content:
                        text = delta.content[0].text.value
                        yield text
                elif event.event == "done":
                    break

    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI API: {e}")
        yield "Извините, произошла ошибка."


async def upload_file_to_openai(file_data):
    file = await client.files.create(
        file=file_data,
        purpose="assistants"
    )
    return file

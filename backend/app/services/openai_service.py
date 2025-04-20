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


async def get_assistant_response(
    user_message: str,
    chat: Chat,
    assistant: Assistant,
    chat_service: ChatService,
    files: [dict] = None,
    images: [dict] = None
) -> AsyncGenerator[str, None]:

    try:
        if not chat.thread_id:
            thread = await client.beta.threads.create()
            thread_id = thread.id
            await chat_service.update_chat(chat.id, thread_id=thread_id)
        else:
            thread_id = chat.thread_id

        content = []
        if user_message:
            content.append({"type": "text", "text": user_message})

        attachments = []
        if files:
            for file in files:
                attachments.append({
                    "file_id": file["file_id"],
                    "tools": [{"type": "code_interpreter"}]
                })

            filenames = ", ".join([file.get("filename", "Неизвестный файл") for file in files])
            content.append({"type": "text", "text": f"(Файлы: {filenames})"})

        # if image_ids:
        #     for image_id in image_ids:
        #         content.append({
        #             "type": "image_file",
        #             "image_file": {"file_id": f"{image_id}"}
        #         })

        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content,
            attachments=attachments or None,
        )

        async with client.beta.threads.runs.stream(thread_id=thread_id, assistant_id=assistant.openai_id) as stream:
            async for event in stream:
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

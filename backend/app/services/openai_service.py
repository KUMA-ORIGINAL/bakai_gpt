import json
import logging
import mimetypes
from typing import AsyncGenerator, List, Optional

from openai import AsyncOpenAI
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
    files: Optional[List[dict]] = None,
    images: Optional[List[dict]] = None
) -> AsyncGenerator[str, None]:
    try:
        thread_id = chat.thread_id
        if not thread_id:
            thread = await client.beta.threads.create()
            thread_id = thread.id
            await chat_service.update_chat(chat.id, thread_id=thread_id)

        attachments = [
            {
                "file_id": file["file_id"],
                "tools": [{"type": "code_interpreter"}]
            }
            for file in (files or [])
        ]

        filenames_text = ""
        if files:
            filenames = ", ".join([file.get("filename", "Неизвестный файл") for file in files])
            filenames_text = f"\n\n(Файл{'ы' if len(files) > 1 else ''}: {filenames})"

        content = [{"type": "text", "text": user_message + filenames_text}]

        if images:
            for image in images:
                content.append({
                    "type": "image_file",
                    "image_file": {
                        "file_id": image["file_id"],
                        "detail": "low"
                    }
                })

        logger.info(f"📤 Sending message: content={content}, attachments={attachments}")

        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content,
            attachments=attachments or None,
        )

        async with client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant.openai_id
        ) as stream:
            async for event in stream:
                if event.event == "thread.message.delta":
                    delta = event.data.delta
                    if delta and delta.content:
                        yield delta.content[0].text.value
                elif event.event == 'thread.run.requires_action':
                    run_id = event.data.id
                    tool_outputs = []

                    for tool in event.data.required_action.submit_tool_outputs.tool_calls:
                        if tool.function.name == "generate_image":
                            args = json.loads(tool.function.arguments)
                            image_url = await generate_image(args["prompt"])
                            tool_outputs.append({
                                "tool_call_id": tool.id,
                                "output": image_url
                            })
                    async with client.beta.threads.runs.submit_tool_outputs_stream(
                            thread_id=thread_id,
                            run_id=run_id,
                            tool_outputs=tool_outputs,
                    ) as tool_stream:
                        async for text in tool_stream.text_deltas:
                            yield text
                elif event.event == "done":
                    break

    except Exception as e:
        logger.exception("❌ Ошибка при запросе к OpenAI API")
        yield "Извините, произошла ошибка."


async def generate_image(prompt: str) -> str:
    logger.info(f"🖼 Генерация изображения по описанию: {prompt}")
    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url


async def upload_file_to_openai(file_data, filename: str = None):
    mime_type, _ = mimetypes.guess_type(filename or getattr(file_data, 'name', ''))

    if mime_type and mime_type.startswith("image/"):
        purpose = "vision"
    else:
        purpose = "assistants"

    file = await client.files.create(
        file=file_data,
        purpose=purpose
    )
    return file

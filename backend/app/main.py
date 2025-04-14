import logging
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from admin import AssistantAdmin, authentication_backend
from config import settings
from api import router as api_router
from create_app import create_app
from models import db_helper

logging.basicConfig(
    format=settings.logging.log_format,
)

main_app = create_app(
    create_custom_static_urls=True,
)

main_app.include_router(
    api_router,
)

admin = Admin(main_app, db_helper.engine, authentication_backend=authentication_backend)
admin.add_view(AssistantAdmin)


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )

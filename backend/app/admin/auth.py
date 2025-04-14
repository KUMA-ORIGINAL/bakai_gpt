from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if username == settings.admin.USERNAME and password == settings.admin.PASSWORD:
            request.session.update({"token": "valid"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("token") == "valid"


authentication_backend = AdminAuth(secret_key=settings.admin.SECRET_KEY)

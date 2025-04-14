from sqladmin import Admin, ModelView

from models import Assistant


class AssistantAdmin(ModelView, model=Assistant):
    column_list = [Assistant.id, Assistant.name, Assistant.description]
    name = "Ассистент"
    name_plural = "Ассистенты"

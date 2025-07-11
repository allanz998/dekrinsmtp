from django.contrib import admin
from .models import TelegramContact
from unfold.admin import ModelAdmin

@admin.register(TelegramContact)
class TelegramContactAdmin(ModelAdmin):
    list_display=('chat_id','email_addr') 
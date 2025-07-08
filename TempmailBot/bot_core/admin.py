from django.contrib import admin
from .models import TelegramContact

@admin.register(TelegramContact)
class TelegramContactAdmin(admin.ModelAdmin):
    list_display=('username', 'chat_id')
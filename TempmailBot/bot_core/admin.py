from django.contrib import admin
from .models import TelegramContact
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin

@admin.register(TelegramContact)
class TelegramContactAdmin(ImportExportModelAdmin, ModelAdmin):
    list_display=('chat_id','email_addr') 
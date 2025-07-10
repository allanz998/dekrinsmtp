from django.db import models

# Create your models here.
class TelegramContact(models.Model): 
    chat_id = models.CharField(max_length=255, default='', unique=True)
    email_addr=models.EmailField(default='', unique=True)

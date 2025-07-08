from .models import TelegramContact

def q_lookup(email_addr):
    exact_user=TelegramContact.objects.filter(email_addr=email_addr).first()

    if exact_user:
        return exact_user.chat_id
    else:
        return None


from bot_core.models import TelegramContact
from django.conf import settings
import string
import random

#most functions will reside here.

def retrieve_dem_mails(chat_id):
    """
    Retrieves the email address associated with a user_id in the DB. Called when the user checks their current email address.
    """
    contacts = TelegramContact.objects.filter(chat_id=chat_id).first()
    if not contacts == None:
        return contacts.email_addr
    return None



def is_exists(prefx):
    """
    Checks if an email with the passed user prefix already exists
    """
    contacts = TelegramContact.objects.filter(email_addr__istartswith=f"{prefx}@") 
    if not contacts.exists():
        return False
    else: 
        return True


def create_new_email(chat_id, prefx=None):
    """
    Creates fresh email addresses upon request
    """
    if_exists = TelegramContact.objects.filter(chat_id=chat_id).first()
    new_email=new_mail_gen(prefx)

    if if_exists:
        if_exists.email_addr=new_email
        if_exists.save()
    else:
        new_contact=TelegramContact(
            chat_id=chat_id,
            email_addr= new_email, 
        )
        new_contact.save()

    return new_email





def new_mail_gen(prefx=None, length=10):
    
    """  
    Core email generation logic
    """
    if not prefx == None:
        new_mail=f"{prefx}@{settings.BASE_DOMAIN}"
    else:
        username = ''.join(
            random.choices(
                string.ascii_lowercase + string.digits,
                k=length
            )
        )
        new_mail=f"{username}@{settings.BASE_DOMAIN}"

    print(new_mail)
    return new_mail



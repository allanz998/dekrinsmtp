import asyncio
import json
import html
from django.core.management.base import BaseCommand
from aiogram import Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton 
from aiogram.types.input_file import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton

) 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aio_pika import connect, IncomingMessage
from django.conf import settings
from asgiref.sync import sync_to_async
from bot_core.lookup import q_lookup
from bot_core.fun import create_new_email, retrieve_dem_mails, is_exists

 
dp = Dispatcher() 
botx=Bot(token=settings.BOT, default=DefaultBotProperties(parse_mode="HTML"))

class Form(StatesGroup):
    name_prefx = State()



class Command(BaseCommand):
    help = 'Listens to RabbitMQ for emails and forwards to Telegram'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize with your actual credentials
        self.TELEGRAM_BOT_TOKEN = settings.BOT 
        self.bot = Bot(token=self.TELEGRAM_BOT_TOKEN)
        
    async def on_email_message(self, message: IncomingMessage):
        async with message.process():
            try:
                email = json.loads(message.body.decode())
                self.stdout.write(f"Processing email: {email['subject']}")

                #Look up the user_id with this email addr:
                reciepient=email['toAddress']
                chat_id = await sync_to_async(q_lookup)(reciepient)

                text = (
                    f"📧 <b>{(email['subject'])}</b>\n\n"
                    f"From: <code>{html.escape(email['from'])}</code>\n\n"
                    f"{html.escape(email['body'])}"
                )

                if chat_id:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        parse_mode="HTML"
                    )
            except Exception as e:
                self.stderr.write(f"Error processing message: {str(e)}")
 

    @dp.message(F.text.lower() == '/start')
    async def msg(message: Message):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="📥 Get Email",
            callback_data="new_email"
        ))
        builder.add(InlineKeyboardButton(
            text="📮 My Email",
            callback_data="list_emails"
        ))
        builder.add(InlineKeyboardButton(
            text="User Guide",
            callback_data="guide"
        ))
        builder.adjust(2)
        await message.answer(f'👋Hello, Welcome to {settings.APP_NAME} by {settings.DEVELOPER}📨\n\nWhat can we do Today?',  reply_markup=builder.as_markup())

    @dp.callback_query(F.data == "new_email")
    async def button1_handler(callback: CallbackQuery, state: FSMContext): 
        await state.set_state(Form.name_prefx)
        await callback.message.answer(f"<b>Enter your nickname: </b>", parse_mode="HTML")

    @dp.message(Form.name_prefx)
    async def user_prefix(message: Message, state: FSMContext):
        prefx=message.text.strip()
        reserved = ['admin', 'support', 'info', 'email', 'agent']
        if len(prefx.split()) > 1:
            await message.reply('This is not allowed. Send me one single name')
            return
        
        if prefx in reserved:
            await message.reply('Username is not available to you. Try a different one')
            return
        
        if '@' in prefx:
            await message.answer('Error!\n\nYou cant include <code>@</code> symbol in your nickname.') 
            return
        
        if prefx.startswith('@'):
            await message.reply('It should not start with <code>@</code> symbol')
            return
        #check related mail in db
        exists = await sync_to_async(is_exists)(prefx) 
        if exists:
            await message.reply(f"<b>An email with this Nickname already exists!\n\nLets Try it once more. Send Nickname: </b>")
        else:
            new_email=await sync_to_async(create_new_email)(chat_id=message.from_user.id, prefx=prefx.lower())
            await message.answer(f"<b>New Address:\n</b> <code>{new_email}</code>\n\nDestroy this address by Clicking again the <b>Get Email</b> Button", parse_mode='HTML')
            await state.clear()



    @dp.callback_query(F.data == "list_emails")
    async def button2_handler(callback: CallbackQuery): 
        mail = await sync_to_async(retrieve_dem_mails)(chat_id=callback.from_user.id)
        if not mail==None and not mail.endswith('example.com'):
            await callback.message.answer(f"<b>Email Address:\n</b> <code>{mail}</code>\n\nThis Email address can last longer untill you Generate a new one.", parse_mode='HTML')
        else:
            await callback.message.answer(f"Looks like you have no address yet. \nClick the <b>Get Email</b> button to create one.", parse_mode='HTML')

    @dp.callback_query(F.data == "guide")
    async def userGuide(callback: CallbackQuery):
        await callback.answer(f'👋Hello, Welcome to {settings.APP_NAME}\n\nGet a disposable Email Address for OTP and other purposes.\n\nOur services are fully supported by AWS, Akamai, Digital Ocean, PayPal among others.\n\n❗️ Avoid abusive Usage.', show_alert=True)

    async def async_main(self):

        
        try:
            connection = await connect("amqp://localhost")
            channel = await connection.channel()
            queue = await channel.declare_queue("email_messages", durable=True)

            await queue.consume(self.on_email_message)
            self.stdout.write("Consumer started. Waiting for emails...")
            await dp.start_polling(botx)
            await asyncio.Future()
        except Exception as e:
            self.stderr.write(f"RabbitMQ connection error: {str(e)}")
            raise

        
    def handle(self, *args, **options):
        
        try:
            asyncio.run(self.async_main())
        except KeyboardInterrupt:
            self.stdout.write("\nShutting Tempmail service...")
        except Exception as e:
            self.stderr.write(f"Fatal error: {str(e)}")
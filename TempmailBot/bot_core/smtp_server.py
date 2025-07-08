
import asyncio
from aiosmtpd.controller import Controller
from email.parser import BytesParser
import json
import aio_pika
from datetime import datetime  

RABBITMQ_URL = "amqp://localhost"
EMAIL_QUEUE = "email_messages"

class EmailHandler:
    async def handle_DATA(self, server, session, envelope):
        try:
            to_address = envelope.rcpt_tos[0]
            from_address = envelope.mail_from
            msg = BytesParser().parsebytes(envelope.content)
            
            email_data = {
                "toAddress": to_address,
                "from": from_address,
                "subject": msg["subject"] or "(no subject)",
                "body": msg.get_payload() or "(no body)",
                "timestamp": datetime.now().isoformat() 
            }
            
            await self.send_to_rabbitmq(email_data)
            return '250 Message accepted for delivery'
        except Exception as e:
            print(f"Error processing email: {e}")
            return '500 Could not process message'



async def run_smtp_server():
    handler = EmailHandler()
    controller = Controller(handler, hostname='127.0.0.1', port=2525)
    controller.start()
    print("SMTP server running on port 2525")
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        controller.stop()




import asyncio
from aiosmtpd.controller import Controller
from email.parser import BytesParser
import json
import aio_pika
from datetime import datetime

RABBITMQ_URL = "amqp://localhost"
EMAIL_QUEUE = "email_messages"

import email
from email.policy import default

class EmailHandler:
    async def handle_DATA(self, server, session, envelope):
        try:
            to_address = envelope.rcpt_tos[0]
            from_address = envelope.mail_from
            
            # Parse with email policy to handle different content types
            msg = email.message_from_bytes(envelope.content, policy=default)
            
            # Extract text content
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_content()
                        break
            else:
                body = msg.get_content()
            
            email_data = {
                "toAddress": to_address,
                "from": from_address,
                "subject": msg["subject"] or "(no subject)",
                "body": body or "(no body)",
                "timestamp": datetime.now().isoformat(),
                "client_ip": session.peer[0]
            }
            
            await self.send_to_rabbitmq(email_data)
            return '250 Message accepted for delivery'
            
        except Exception as e:
            print(f"Error processing email: {str(e)}")
            return '451 Temporary processing error'
        
    async def send_to_rabbitmq(self, email_data):
        connection = await aio_pika.connect(RABBITMQ_URL)
        channel = await connection.channel()
        queue = await channel.declare_queue(EMAIL_QUEUE, durable=True)
        
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(email_data).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=EMAIL_QUEUE
        )
        print(f"Email queued for {email_data['toAddress']}")
        await connection.close()

async def run_smtp_server():
    handler = EmailHandler()
    controller = Controller(
        handler,
        hostname='0.0.0.0',  # Listen externally
        port=25,             # Standard SMTP port
        ident="MySMTP 1.0"    # Server banner
    )
    controller.start()
    print(f"SMTP server running on port {controller.port}")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        controller.stop()

if __name__ == "__main__":
    asyncio.run(run_smtp_server())
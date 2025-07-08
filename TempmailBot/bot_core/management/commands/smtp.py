from django.core.management.base import BaseCommand
from bot_core.smtp_server import run_smtp_server
import asyncio

class Command(BaseCommand):
    help = 'Runs the SMTP email server'

    def handle(self, *args, **options):
        try:
            asyncio.run(run_smtp_server())
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('SMTP server stopped'))
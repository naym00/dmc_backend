import asyncio
import threading
from django.apps import AppConfig


class LogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'log'
    scheduler_lock = asyncio.Lock()
    def ready(self):
        process_flag=True

        print("log scheduler running...")
        from .auto_sync_log import log_updater
        loop = asyncio.get_event_loop()
        try:
            if process_flag:
                loop.run_until_complete(self.async_ready(log_updater))
                process_flag=False
        except Exception as e:
            print("error :",e)

    async def async_ready(self, log_updater):
        async with self.scheduler_lock:
            await log_updater.start()

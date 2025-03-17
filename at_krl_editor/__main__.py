import asyncio
import atexit
import logging
import os
import subprocess
import sys
from typing import Tuple

from at_queue.core.session import ConnectionParameters
from django.core import management
from django.core.asgi import get_asgi_application
from uvicorn import Config
from uvicorn import Server

from at_krl_editor.absolute.django_init import args
from at_krl_editor.absolute.django_init import get_args
from at_krl_editor.core.component import ATKRLEditor

logger = logging.getLogger(__name__)


django_application = get_asgi_application()


def get_editor(args: dict = None) -> Tuple[ATKRLEditor, dict]:
    args = args or get_args()
    no_worker = args.pop("no_worker", False)
    connection_parameters = ConnectionParameters(**args)

    # Создание PID-файла (опционально)
    try:
        if not os.path.exists("/var/run/at_tutoring_skills/"):
            os.makedirs("/var/run/at_tutoring_skills/")

        with open("/var/run/at_tutoring_skills/pidfile.pid", "w") as f:
            f.write(str(os.getpid()))
    except PermissionError:
        pass

    args["no_worker"] = no_worker
    return ATKRLEditor(connection_parameters), args


def start_worker():
    process = subprocess.Popen([sys.executable, "-m", "celery", "-A", "at_krl_editor", "worker", "-l", "info"])

    logger.info("Worker started")

    def kill_worker():
        process.terminate()
        process.wait()
        logger.info("Worker stopped")

    atexit.register(kill_worker)


async def main_with_django(args: dict = None):
    editor, args = get_editor(args=args)

    server_host = args.pop("server_host", "localhost")
    server_port = args.pop("server_port", 8000)

    async def lifespan(app):
        """Пользовательский lifespan для управления asyncio жизненным циклом веб-приложения."""
        logging.basicConfig(level=logging.INFO)

        await editor.initialize()
        await editor.register()

        loop = asyncio.get_event_loop()
        loop.create_task(editor.start())

        if not args.get("no_worker"):
            start_worker()

        yield  # Приложение запущено

    # Обертываем Django-приложение с пользовательским lifespan
    async def app(scope, receive, send):
        if scope["type"] == "lifespan":
            # Обработка событий lifespan
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    # Запуск lifespan
                    async for _ in lifespan(None):
                        pass
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    # Завершение lifespan
                    await send({"type": "lifespan.shutdown.complete"})
                    break
        else:
            # Обработка HTTP-запросов через Django
            await django_application(scope, receive, send)

    # Конфигурация и запуск сервера Uvicorn
    config = Config(
        app=app,  # Передаем обернутое ASGI-приложение
        host=server_host,
        port=server_port,
        lifespan="on",  # Включаем поддержку lifespan
    )
    server = Server(config=config)
    await server.serve()


if __name__ == "__main__":
    management.call_command("migrate")

    asyncio.run(main_with_django(args=args))

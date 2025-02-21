import asyncio
import logging
import os
from typing import Tuple

import django
from at_queue.core.session import ConnectionParameters
from django.core import management
from django.core.asgi import get_asgi_application
from uvicorn import Config
from uvicorn import Server

from at_krl_editor.core.arguments import ARGS_TO_ENV_MAPPING
from at_krl_editor.core.arguments import get_args
from at_krl_editor.core.component import ATKrlEditor
from at_krl_editor.utils.settings import get_django_settings_module

settings_module = get_django_settings_module()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

args = get_args()
for arg_name, arg_value in args.items():
    env_arg_name = ARGS_TO_ENV_MAPPING.get(arg_name)
    if env_arg_name and arg_value:
        os.environ[env_arg_name] = str(arg_value)

django.setup()

django_application = get_asgi_application()


def get_editor(args: dict = None) -> Tuple[ATKrlEditor, dict]:
    args = args or get_args()
    connection_parameters = ConnectionParameters(**args)

    # Создание PID-файла (опционально)
    try:
        if not os.path.exists("/var/run/at_tutoring_skills/"):
            os.makedirs("/var/run/at_tutoring_skills/")

        with open("/var/run/at_tutoring_skills/pidfile.pid", "w") as f:
            f.write(str(os.getpid()))
    except PermissionError:
        pass

    return ATKrlEditor(connection_parameters), args


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

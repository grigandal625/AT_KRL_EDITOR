import os
import subprocess


def get_django_settings_module() -> str:
    # Поиск директории с manage.py
    def find_manage_dir() -> str:
        current_dir = os.path.abspath(os.getcwd())
        while True:
            manage_path = os.path.join(current_dir, "manage.py")
            if os.path.isfile(manage_path):
                return current_dir
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                return None
            current_dir = parent_dir

    manage_dir = find_manage_dir()
    if not manage_dir:
        # Проект используется как приложение, настройки должны быть заданы вручную
        return None

    result = (
        subprocess.Popen(
            " ".join(["python", os.path.join(manage_dir, "manage.py"), "get_settings_module"]),
            shell=True,
            stdout=subprocess.PIPE,
        )
        .stdout.read()
        .decode()[:-1]
    )
    return result

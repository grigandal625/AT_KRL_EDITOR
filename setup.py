import os
import shutil
from setuptools import setup
from setuptools.command.install import install

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        
        # Проверяем активацию extra через флаги установки
        base_server_enabled = any(
            'base_server' in flag.lower()
            for flag in self.distribution.install_requires
        )

        base_server_src = os.path.join(os.path.dirname(__file__), "at_krl_editor", "base_server")
        dest = os.path.join(os.getcwd(), "base_server")

        if base_server_enabled:
            if os.path.exists(base_server_src):
                shutil.copytree(base_server_src, dest, dirs_exist_ok=True)
                print(f"Django template copied to {dest}")
            else:
                print(f"Warning: base_server template not found at {base_server_src}")
        else:
            if os.path.exists(dest):
                shutil.rmtree(dest)
                print(f"Cleaned {dest} as 'base_server' extra was not requested")

setup(
    cmdclass={
        "install": PostInstallCommand,
    },
)
import os
import shutil
import sys
from setuptools import setup
from setuptools.command.install import install

class PostInstallCommand(install):
    def run(self):
        # Определяем активацию extra ДО установки
        base_server_enabled = any(
            arg.strip().startswith(('--extras=base_server', '-E base_server', '--extras base_server')) 
            for arg in sys.argv
        )

        install.run(self)  # Стандартная установка

        base_server_src = os.path.join(
            os.path.dirname(__file__), 
            "at_krl_editor", 
            "base_server"
        )
        dest = os.path.join(os.getcwd(), "base_server")

        if base_server_enabled:
            if os.path.exists(base_server_src):
                shutil.copytree(
                    base_server_src, 
                    dest,
                    dirs_exist_ok=True
                )
                print(f"✓ Base server template installed to: {dest}")
            else:
                print(f"⚠️  Source template not found: {base_server_src}")
        else:
            # Удаляем из site-packages
            installed_path = os.path.join(
                self.install_lib, 
                "at_krl_editor",
                "base_server"
            )
            
            shutil.rmtree(installed_path)
            print(f"✓ Removed base_server from package (extra not requested)")

setup(
    cmdclass={
        "install": PostInstallCommand,
    },
)
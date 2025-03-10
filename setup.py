import os
import shutil
import sys
import logging
from setuptools import setup
from setuptools.command.install import install

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('post-install')

class PostInstallCommand(install):
    def run(self):
        logger.info("\n=== Starting installation ===")
        
        # Анализ аргументов
        logger.info(f"System arguments: {sys.argv}")
        base_server_enabled = any(
            'base_server' in arg.lower() 
            for arg in sys.argv
        )
        logger.info(f"Base server enabled: {base_server_enabled}")

        # Стандартная установка
        install.run(self)

        # Пути для отладки
        base_server_src = os.path.join(
            os.path.dirname(__file__), 
            "at_krl_editor", 
            "base_server"
        )
        installed_path = os.path.join(
            self.install_lib, 
            "at_krl_editor",
            "base_server"
        )
        dest_path = os.path.join(os.getcwd(), "base_server")

        logger.info(f"Source path: {base_server_src}")
        logger.info(f"Installed path: {installed_path}")
        logger.info(f"Destination path: {dest_path}")

        # Логика обработки base_server
        if base_server_enabled:
            logger.info("Processing base_server extra...")
            if os.path.exists(base_server_src):
                shutil.copytree(base_server_src, dest_path, dirs_exist_ok=True)
                logger.info(f"Copied template to {dest_path}")
            else:
                logger.error("Source template not found!")
        else:
            logger.info("Cleaning base_server files...")
            if os.path.exists(installed_path):
                logger.info(f"Removing {installed_path}")
                shutil.rmtree(installed_path)
            if os.path.exists(dest_path):
                logger.info(f"Removing {dest_path}")
                shutil.rmtree(dest_path)

        logger.info("=== Installation completed ===\n")

setup(
    cmdclass={
        "install": PostInstallCommand,
    },
)
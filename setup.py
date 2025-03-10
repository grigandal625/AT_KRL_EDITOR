import logging
import os
import shutil
import sys
from pathlib import Path
from setuptools import setup
from setuptools.command.install import install

LOG_FILE = Path(__file__).parent / "install.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True
)
logger = logging.getLogger()

class PostInstallCommand(install):
    def run(self):
        logger.info("=== PostInstallCommand started ===")
        
        try:
            # Определяем активацию extra
            base_server_enabled = "[base_server]" in " ".join(sys.argv).lower()
            logger.info(f"Base server enabled: {base_server_enabled}")
            
            # Стандартная установка
            install.run(self)
            
            # Пути для обработки
            src_path = Path(__file__).parent / "at_krl_editor" / "base_server"
            dest_path = Path.cwd() / "base_server"
            installed_path = Path(self.install_lib) / "at_krl_editor" / "base_server"
            
            logger.info(f"Source: {src_path}")
            logger.info(f"Destination: {dest_path}")
            logger.info(f"Installed path: {installed_path}")

            if base_server_enabled:
                # Копирование шаблона
                if src_path.exists():
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                    logger.info("Template copied successfully")
                else:
                    logger.error("Template source not found!")
            else:
                # Удаление из site-packages
                if installed_path.exists():
                    shutil.rmtree(installed_path)
                    logger.info("Removed from site-packages")
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                    logger.info("Removed from project directory")

        except Exception as e:
            logger.exception("Critical error during installation:")
            raise

        logger.info("=== PostInstallCommand completed ===\n")

setup(
    cmdclass={"install": PostInstallCommand},
)
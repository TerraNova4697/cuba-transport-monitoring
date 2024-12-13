import os
import logging
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class LoggerMaker:
    def __init__(self):
        self._BASE_PATH = Path(__file__).parent
        self._format = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)s - %(message)s"
        self._logger_name = "teltonika_logger"
        self._logs_path = self._BASE_PATH
        self.create_directories_if_not_exist()

    def create_directories_if_not_exist(self):
        logs_path = os.path.join(self._BASE_PATH, 'logs')
        Path(logs_path).mkdir(parents=True, exist_ok=True)
        self._logs_path = logs_path

    def make(self) -> Logger:
        print("Создание логгера")
        teltonika_logger = logging.getLogger(self._logger_name)

        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(self._logs_path, 'teltonika.log'), when="midnight", backupCount=31, encoding="utf-8"
        )
        file_handler.setFormatter(
            logging.Formatter(self._format)
        )
        teltonika_logger.addHandler(file_handler)
        teltonika_logger.setLevel(logging.INFO)
        return teltonika_logger

logger = LoggerMaker().make()




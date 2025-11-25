import csv
import logging
from datetime import timedelta

import colorlog
from pydantic_settings import BaseSettings
from pytesseract import pytesseract


class TimeZoneAwareFormatter(colorlog.ColoredFormatter):
    def formatTime(self, record, datefmt=None):
        """
        Форматирует время с учетом часового пояса.
        """
        ct = self.converter(record.created) + timedelta(hours=3)
        return ct.strftime("%Y-%m-%d %H:%M:%S")

    def converter(self, timestamp):
        """
        Конвертирует timestamp в datetime.
        """
        import datetime
        # Получаем datetime из timestamp
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        return dt


handler = colorlog.StreamHandler()
handler.setFormatter(TimeZoneAwareFormatter(
    fmt='%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    log_colors={
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red',
    },
))

logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)


class CsvLogHandler(logging.Handler):
    def __init__(self, filename, mode='a', encoding=None):
        super().__init__()
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.headers = ['Level', 'Time', 'Message']
        # Проверяем, существует ли файл и нужно ли добавлять заголовки
        try:
            with open(self.filename, 'x', newline='', encoding=self.encoding) as file:
                writer = csv.writer(file, delimiter=';')
                if self.headers:
                    writer.writerow(self.headers)
        except FileExistsError:
            pass

    def emit(self, record):
        with open(self.filename, self.mode, encoding=self.encoding, newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow([record.levelname, record.asctime, record.msg])


csv_handler = CsvLogHandler('log.csv')
logging.getLogger().addHandler(csv_handler)


class Settings(BaseSettings):
    MAX_FILE_SIZE_MB: int
    UUID_TEST_CHECK: str
    PDF_TIMEOUT: int = 120

    _ocr_reader: pytesseract = pytesseract

    @property
    def ocr_reader(self) -> pytesseract:
        return pytesseract


settings = Settings()

from typing import NoReturn

import chardet
from fastapi import HTTPException, UploadFile
import logging

from config import settings


def is_text_file(raw_data: bytes):
    """
    Определяет, является ли файл текстовым по его содержимому
    """
    try:
        # Проверяем на наличие null-байтов (признак бинарного файла)
        if b'\x00' in raw_data:
            return False

        # Пытаемся определить кодировку
        encoding_result = chardet.detect(raw_data)
        confidence = encoding_result.get('confidence', 0)

        # Если уверенность в определении кодировки высокая, скорее всего это текст
        return confidence > 0.7

    except Exception as e:
        return False


def check_empty_file(file: bytes) -> bool:
    if file == b'':
        return True

    return False


async def validate_document(file: UploadFile) -> UploadFile | NoReturn:
    file_size_mb = file.size / (1024 * 1024)
    allowed_content_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/msword",
        "text/plain",
        "text/markdown",
        "application/json",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    }
    file_content = await file.read(1024)
    await file.seek(0)

    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File is too large", headers={"content_type": file.content_type})

    if check_empty_file(file_content):
        raise HTTPException(status_code=400, detail="Document is empty",
                            headers={"content_type": "text/plain", "tokens": 0})

    if file.content_type in allowed_content_types or is_text_file(file_content):
        return file
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported document format",
            headers={"content_type": file.content_type}
        )
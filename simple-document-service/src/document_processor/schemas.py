from io import BytesIO
from typing import BinaryIO

from fastapi import Header, UploadFile, File
from pydantic import BaseModel


# class DocumentInput(BaseModel):
#     tg_id: int = Header(..., alias="x-tg-id")
#     file: UploadFile = File(...)


class DocumentOutput(BaseModel):
    tg_id: int
    content: str

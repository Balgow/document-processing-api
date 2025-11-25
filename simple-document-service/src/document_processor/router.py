import asyncio
import datetime
import logging
import time
from typing import BinaryIO
from urllib.parse import unquote

import aiofiles
from fastapi import APIRouter, UploadFile, Depends, HTTPException

from document_processor.dependencies import validate_document
from document_processor.schemas import DocumentOutput
from document_processor.utils import load_document_as_text

document_processor_router = APIRouter()


@document_processor_router.post("/docshandle/{tg_id}", response_model=DocumentOutput)
async def process_document(tg_id: int, file: UploadFile = Depends(validate_document)):
    try:
        document_bytes: BinaryIO = file.file
        filename = unquote(file.filename)
        start = time.time()

        text, tokens = await load_document_as_text(document_bytes, file.content_type)
        logging.info(
            f"time {(time.time() - start):.2f}s | tg {tg_id} | tokens {tokens} | type {file.content_type} | file {filename}")

        async with aiofiles.open(
                f"./uploads/{datetime.datetime.now().strftime('%d-%m-%Y %H-%M-%S')} {filename} OUTPUT.txt",
                'wb') as out_file:
            await out_file.write(text.encode("utf-8"))

        return {"tg_id": tg_id, "content": text}

    except HTTPException as e:
        if isinstance(e.headers, dict):
            e.headers.update({"content_type": file.content_type})
        else:
            e.headers = {"content_type": file.content_type}
        raise e

    except TimeoutError:
        logging.warning(f"Timeout error: {file.filename}")
        raise HTTPException(status_code=400, detail="Document is too large", headers={"content_type": file.content_type})

    except Exception as e:
        logging.error(msg="Unexpected error:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e), headers={"content_type": file.content_type})

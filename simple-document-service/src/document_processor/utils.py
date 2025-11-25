import asyncio
import multiprocessing
import signal
import logging
import sys
import tiktoken

from typing import BinaryIO
from contextlib import suppress


from fastapi import HTTPException

from config import settings
from document_processor.readers import pdf_reader, docx_reader, excel_reader, csv_reader, pptx_reader, xls_reader, \
    ultimate_text_reader, image_reader, doc_reader

PDF_TIMEOUT = settings.PDF_TIMEOUT


def tokens_counter(text: str) -> int:
    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    encoded = encoding.encode(text)
    return len(encoded)


def process_wrapper(result_queue, content):
    # Глобальная переменная для контроля завершения
    should_exit = False

    def signal_handler(signum, frame):
        nonlocal should_exit
        should_exit = True

    try:
        # Установка обработчика сигналов
        signal.signal(signal.SIGTERM, signal_handler)

        # Выполнение основной работы
        if not should_exit:
            result = pdf_reader(content)
            result_queue.put(result)

    except Exception as e:
        logging.error(f"Error in process: {e.__repr__()}", exc_info=True)
        with suppress(Exception):
            result_queue.put(e)
    finally:
        # Очистка ресурсов
        with suppress(Exception):
            result_queue.close()

        if should_exit:
            # Более мягкое завершение процесса
            logging.shutdown()
            sys._exit(0)


def cleanup_process(proc):
    """Корректное завершение процесса"""
    with suppress(Exception):
        proc.terminate()
        proc.join(timeout=3)
        if proc.is_alive():
            proc.kill()
            proc.join()


async def process_with_timeout(pdf_content, timeout):
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=process_wrapper,
        args=(result_queue, pdf_content)
    )

    try:
        process.start()
        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < timeout:
            if not result_queue.empty():
                result = result_queue.get()
                if isinstance(result, Exception):
                    raise result

                return result
            await asyncio.sleep(0.1)

        raise asyncio.TimeoutError()

    except Exception as e:
        logging.error(f"Process error: {e.__repr__()}")
        raise

    finally:
        if process.is_alive():
            cleanup_process(process)

        with suppress(Exception):
            result_queue.close()


async def load_document_as_text(binary_doc: BinaryIO, mime_type: str) -> tuple[str, int]:
    match mime_type:
        case "application/pdf":
            pdf_content = binary_doc.read()
            doc_content = await process_with_timeout(pdf_content, timeout=PDF_TIMEOUT)

        case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc_content = await asyncio.to_thread(docx_reader, binary_doc)

        case "application/msword":
            doc_content = await asyncio.to_thread(doc_reader, binary_doc)

        case "text/plain" | "text/markdown" | "application/json":
            doc_content = await asyncio.to_thread(ultimate_text_reader, binary_doc)

        case "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            doc_content = await asyncio.to_thread(excel_reader, binary_doc)

        case "application/vnd.ms-excel":
            doc_content = await asyncio.to_thread(xls_reader, binary_doc)

        case "text/csv":
            doc_content = await asyncio.to_thread(csv_reader, binary_doc)

        case "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            doc_content = await asyncio.to_thread(pptx_reader, binary_doc)

        case _ if "text" in mime_type:
            doc_content = await asyncio.to_thread(ultimate_text_reader, binary_doc)

        case _ if "image" in mime_type:
            doc_content = await asyncio.to_thread(image_reader, binary_doc)

        case _:
            try:
                doc_content = await asyncio.to_thread(ultimate_text_reader, binary_doc)
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported document format",
                    headers={"content_type": mime_type}
                )

    tokens = tokens_counter(doc_content)

    if tokens > 180_000:
        raise HTTPException(
            status_code=400,
            detail="Document is too large",
            headers={"content_type": mime_type, "tokens": tokens}
        )
    elif 0 <= tokens <= 3:
        raise HTTPException(
            status_code=400,
            detail="Document is empty",
            headers={"content_type": mime_type, "tokens": tokens}
        )

    return doc_content, tokens


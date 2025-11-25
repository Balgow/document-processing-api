import datetime
import io
import logging
import time
from urllib.parse import unquote

import aiofiles
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse

from config import settings
from document_processor.router import document_processor_router

app = FastAPI()
app.include_router(document_processor_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if request.method == "POST":
        body = await request.body()
        request._body = body  # Прямое присвоение для сохранения тела в объекте запроса
        request._stream = io.BytesIO(body)  # Создаем новый поток из тела для чтения
        form = await request.form()
        file = form["file"]
        filename = unquote(file.filename)

        async with aiofiles.open(f"./uploads/{datetime.datetime.now().strftime('%d-%m-%Y %H-%M-%S')} {filename}", 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        if request.client:
            logging.info(f"Request: {request.url.path} | {request.method} | {request.client.host} | {request.client.port} | {filename} |{request.headers}")

    time_start = time.time()

    response = await call_next(request)
    if response.status_code < 200 or response.status_code >= 300:
        logging.info(f"Warning or Error time wasted: {(time.time() - time_start):.2f}s")

    return response


@app.get("/health/{uuid}")
async def health(uuid: str):
    try:
        if uuid == settings.UUID_TEST_CHECK:
            return JSONResponse(status_code=200, content={"message": "OK"})
        else:
            logging.error(f"SOMEBODY TRIED TO ACCESS HEALTHCHECK WITH WRONG UUID {uuid}")
            return JSONResponse(status_code=403, content={"message": "Forbidden"})
    except Exception as e:
        logging.error(f"Healthcheck failed", exc_info=True)
        return JSONResponse(status_code=500, content={"message": "Error"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    chars = exc.headers.get('chars')
    tokens = exc.headers.get('tokens')
    chars_or_tokens = f"chars {chars}" if chars is not None else f"tokens {tokens}"

    logging.warning(
        f"Warning: {exc.detail} | id {request.path_params.get('tg_id')} | filetype {exc.headers.get('content_type')} | {chars_or_tokens}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Warning: {exc.detail}"},
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc):
    logging.error(f"Error: {exc} for {request.path_params}")
    return JSONResponse(
        status_code=500,
        content={"message": f"Error: {exc}"},
    )


if __name__ == "__main__":
    uvicorn.run(app)

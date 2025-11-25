FROM python:3.12.8-slim

WORKDIR /usr/src/simple-document-service

ENV PYTHONPATH=/usr/src/simple-document-service/src

COPY requirements/base.txt /requirements/

RUN apt-get update && \
    apt update &&  \
    apt install -y curl &&\
    pip install --upgrade pip && \
    apt install -y libfontconfig1 && \
    apt install tesseract-ocr -y && \
    apt install libtesseract-dev -y && \
    apt install tesseract-ocr-rus && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -r /requirements/base.txt && \
    pip install --no-cache-dir optimum[onnxruntime] rapidfuzz && \
    rm -rf /root/.cache/pip
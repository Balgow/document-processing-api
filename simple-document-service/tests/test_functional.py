import io

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_xlsx():
    with open("tests/files/xlsx.xlsx", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test.xlsx", binary_io, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 200


def test_read_xlsx_large():
    with open("tests/files/xlsx_large.xlsx", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": (
        "test_large.xlsx", binary_io, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Warning: Document is too large"}


def test_read_xlsx_empty():
    with open("tests/files/xlsx_empty.xlsx", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": (
        "test_empty.xlsx", binary_io, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Warning: Document is empty"}


def test_read_pdf():
    with open("tests/files/pdf.pdf", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test.pdf", binary_io, "application/pdf")},
    )

    assert response.status_code == 200


def test_read_pdf_large():
    with open("tests/files/pdf_large.pdf", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test_large.pdf", binary_io, "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Warning: Document is too large"}


def test_read_pdf_empty():
    with open("tests/files/pdf_empty.pdf", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test_empty.pdf", binary_io, "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Warning: Document is empty"}


def test_pdf_pics():
    with open("tests/files/pdf_pics.pdf", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test_pics.pdf", binary_io, "application/pdf")},
    )

    assert response.status_code == 200


def test_read_txt():
    with open("tests/files/txt.txt", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test.txt", binary_io, "text/plain")},
    )

    assert response.status_code == 200


def test_read_txt_empty():
    with open("tests/files/txt_empty.txt", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test_empty.txt", binary_io, "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Warning: Document is empty"}


def test_read_txt_large():
    with open("tests/files/txt_large.txt", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test_large.txt", binary_io, "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"message": "Warning: Document is too large"}


def test_read_md():
    with open("tests/files/md.md", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test.md", binary_io, "text/markdown")},
    )

    assert response.status_code == 200


def test_read_xls():
    with open("tests/files/xls.xls", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test.xls", binary_io, "application/vnd.ms-excel")},
    )

    assert response.status_code == 200


def test_read_doc():
    with open("tests/files/doc.doc", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test.doc", binary_io, "application/msword")},
    )

    assert response.status_code == 200


def test_read_docx():
    with open("tests/files/docx.docx", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": (
        "test.docx", binary_io, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )

    assert response.status_code == 200


def test_read_csv():
    with open("tests/files/csv.csv", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": ("test.csv", binary_io, "text/csv")},
    )

    assert response.status_code == 200


def test_read_pptx():
    with open("tests/files/pptx.pptx", 'rb') as file:
        binary_io = io.BytesIO(file.read())

    response = client.post(
        "/docshandle/2222222",
        files={"file": (
        "test.pptx", binary_io, "application/vnd.openxmlformats-officedocument.presentationml.presentation")},
    )

    assert response.status_code == 200

from io import BytesIO

import cv2
import numpy as np
from fitz import Document
from rapidfuzz import fuzz


def estimate_text_density(doc: Document) -> int:
    """Примерное распознавание количества символов на картинке"""
    total_char_count = 0

    for page in doc:
        for image_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            image_stream = BytesIO(image_bytes)
            image_stream.seek(0)

            # Convert the byte stream to a numpy array
            image_array = np.frombuffer(image_stream.read(), dtype=np.uint8)
            if image_array.size == 0:
                continue

            # Decode the image
            image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
            if image is None:
                continue

            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY_INV, 11, 2)

            # Apply morphological operations to highlight text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # Find contours
            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filter and count contours that could be text
            text_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]

            # Estimate character count
            total_char_count += sum([cv2.boundingRect(cnt)[2] // 10 for cnt in text_contours])

    return total_char_count


def rectangles_intersect(rect1: list, rect2: list):
    # Нормализация координат для первого прямоугольника
    x1_min = min(rect1[0], rect1[2])
    y1_min = min(rect1[1], rect1[3])
    x1_max = max(rect1[0], rect1[2])
    y1_max = max(rect1[1], rect1[3])

    # Нормализация координат для второго прямоугольника
    x2_min = min(rect2[0], rect2[2])
    y2_min = min(rect2[1], rect2[3])
    x2_max = max(rect2[0], rect2[2])
    y2_max = max(rect2[1], rect2[3])

    # Проверка: если один прямоугольник находится левее другого
    if x1_max < x2_min or x2_max < x1_min:
        return False

    # Проверка: если один прямоугольник находится выше другого
    if y1_max < y2_min or y2_max < y1_min:
        return False

    # Если ни одно из условий не выполнено, прямоугольники пересекаются
    return True


def find_partial_match_end_index(needle: str, haystack: str):
    """
    Ищет позицию окончания наилучшего совпадения needle в haystack
    с использованием fuzz.partial_ratio (в данном случае аналогом является fuzz.ratio,
    поскольку окно имеет ту же длину, что и needle).

    Возвращает:
      - best_end_index: индекс окончания найденного совпадения (если совпадение найдено, иначе -1)
      - best_score: оценка схожести (от 0 до 100)
    """
    best_score = -1
    best_end_index = -1
    n_len = len(needle)

    # Перебираем все возможные окна в haystack длиной, равной длине needle.
    for i in range(0, len(haystack) - n_len + 1):
        window = haystack[i:i + n_len]
        score = fuzz.partial_ratio(needle, window)

        if score > best_score:
            best_score = score
            best_end_index = i + n_len  # конец текущего окна

    return best_end_index

"""
processing.py
Funkcje przetwarzania obrazu: detekcja dokumentu, kadrowanie perspektywiczne,
efekt skanera. Brak zależności od Streamlit.
"""

from typing import Optional, Tuple

import cv2
import numpy as np


def order_points(points: np.ndarray) -> np.ndarray:
    """Sortuje 4 punkty: lewy-górny, prawy-górny, prawy-dolny, lewy-dolny."""
    rect = np.zeros((4, 2), dtype="float32")
    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]
    rect[2] = points[np.argmax(s)]
    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmax(diff)]
    return rect


def four_point_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Wykonuje transformację perspektywiczną na podstawie 4 punktów."""
    rect = order_points(points)
    (tl, tr, br, bl) = rect
    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(width_a), int(width_b))
    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(height_a), int(height_b))
    dst = np.array(
        [[0, 0], [max_width - 1, 0],
         [max_width - 1, max_height - 1], [0, max_height - 1]],
        dtype="float32",
    )
    matrix = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, matrix, (max_width, max_height))


def detect_document_contour(
    image: np.ndarray, min_area_ratio: float = 0.08
) -> Optional[np.ndarray]:
    """
    Automatycznie wykrywa kontur dokumentu (kartki) na zdjęciu.
    Zwraca 4 punkty narożne w oryginalnej skali lub None jeśli nie znaleziono.
    """
    original_h, original_w = image.shape[:2]
    image_area = float(original_h * original_w)
    target_height = 1000
    scale = original_h / target_height if original_h > target_height else 1.0
    resized = (
        cv2.resize(image, (int(original_w / scale), int(original_h / scale)))
        if scale > 1.0
        else image
    )

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edge_maps = [
        cv2.Canny(blurred, 30, 120),
        cv2.Canny(blurred, 50, 170),
    ]
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 15
    )
    edge_maps.append(cv2.bitwise_not(thresh))

    best_box = None
    best_area = 0.0
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    for edge_map in edge_maps:
        combined = cv2.morphologyEx(edge_map, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(combined, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:40]
        for contour in contours:
            if len(contour) < 4:
                continue
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect).astype("float32")
            box_area = cv2.contourArea(box) * (scale ** 2)
            if box_area < image_area * min_area_ratio:
                continue
            if box_area > best_area:
                best_area = box_area
                best_box = box

    return best_box * scale if best_box is not None else None


def expand_quad(
    points: np.ndarray, pad_ratio: float, image_shape: tuple
) -> np.ndarray:
    """Rozszerza czworobok o podany współczynnik (margines auto)."""
    if pad_ratio <= 0:
        return points.astype("float32")
    h, w = image_shape[:2]
    center = np.mean(points, axis=0)
    expanded = center + (points - center) * (1.0 + pad_ratio)
    expanded[:, 0] = np.clip(expanded[:, 0], 0, w - 1)
    expanded[:, 1] = np.clip(expanded[:, 1], 0, h - 1)
    return expanded.astype("float32")


def enhance_scanned_look(image: np.ndarray, threshold: int) -> np.ndarray:
    """Konwertuje obraz do czarno-białego efektu skanera."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)[1]


def decode_uploaded_image(image_bytes: bytes) -> np.ndarray:
    """Dekoduje bajty obrazu do tablicy numpy (BGR)."""
    np_bytes = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Nie udało się wczytać obrazu.")
    return image


def process_auto(
    image: np.ndarray,
    threshold: int,
    min_area_ratio: float,
    auto_padding_ratio: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Tryb automatyczny: wykryj dokument → przytnij perspektywicznie → skanuj.
    Zwraca (obraz_przycięty_kolor, obraz_skan_bw).
    """
    contour = detect_document_contour(image, min_area_ratio=min_area_ratio)
    if contour is None:
        raise ValueError(
            "Nie wykryto dokumentu. Zmień czułość lub użyj trybu ręcznego."
        )
    contour = expand_quad(contour, auto_padding_ratio, image.shape)
    warped = four_point_transform(image, contour)
    return warped, enhance_scanned_look(warped, threshold)


def process_manual(
    image: np.ndarray,
    points: np.ndarray,
    threshold: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Tryb ręczny: przytnij perspektywicznie wg podanych punktów → skanuj.
    Zwraca (obraz_przycięty_kolor, obraz_skan_bw).
    """
    warped = four_point_transform(image, points)
    return warped, enhance_scanned_look(warped, threshold)

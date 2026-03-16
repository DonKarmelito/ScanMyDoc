"""
canvas_utils.py
Pomocnicze funkcje do obsługi streamlit-drawable-canvas.
Brak zależności od Streamlit (poza typem PIL.Image jako zwracaną wartością).
"""

from typing import Tuple

import cv2
import numpy as np
from PIL import Image


def build_canvas_image(
    image_bgr: np.ndarray, max_width: int = 700
) -> Tuple[Image.Image, float, float]:
    """
    Skaluje obraz BGR do wyświetlenia na canvasie (max szerokość: max_width px).

    Zwraca:
        pil_image  – obraz PIL w RGB gotowy do canvas background_image
        scale_x    – współczynnik skalowania X (canvas → oryginał)
        scale_y    – współczynnik skalowania Y (canvas → oryginał)
    """
    h, w = image_bgr.shape[:2]
    scale = min(max_width / w, 1.0)
    display_w = int(w * scale)
    display_h = int(h * scale)
    resized = cv2.resize(image_bgr, (display_w, display_h), interpolation=cv2.INTER_AREA)
    pil_image = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
    return pil_image, w / display_w, h / display_h


def extract_points_from_canvas(canvas_json: dict) -> list[tuple[float, float]]:
    """
    Wyciąga współrzędne środków punktów (circles) z JSON canvasa.

    Zwraca listę krotek (x, y) w układzie współrzędnych canvasa.
    """
    objects = (canvas_json or {}).get("objects", [])
    points: list[tuple[float, float]] = []
    for obj in objects:
        if obj.get("type") != "circle":
            continue
        x = float(obj.get("left", 0.0))
        y = float(obj.get("top", 0.0))
        r = float(obj.get("radius", 0.0))
        sx = float(obj.get("scaleX", 1.0))
        sy = float(obj.get("scaleY", 1.0))
        points.append((x + r * sx, y + r * sy))
    return points

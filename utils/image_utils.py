"""Image helpers shared by GUI screens."""

import sys
from pathlib import Path

import cv2
import numpy as np
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont


def _font_path():
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base_dir / "assets" / "fonts" / "Vazirmatn-Regular.ttf"


def draw_persian_text(image, text, position, font_size=24, color=(0, 255, 0)):
    """Draw right-to-left Persian text on an OpenCV BGR image using Vazirmatn."""
    reshaped_text = arabic_reshaper.reshape(text)
    display_text = get_display(reshaped_text)

    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    drawer = ImageDraw.Draw(pil_image)
    font = ImageFont.truetype(_font_path(), font_size)

    drawer.text(
        position,
        display_text,
        font=font,
        fill=color[::-1],
        anchor="ra",
    )

    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

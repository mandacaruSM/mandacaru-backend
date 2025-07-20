# backend/apps/bot_telegram/utils/ocr_utils.py
# Módulo de OCR melhorado com Tesseract + OpenCV + Pillow

import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


def preprocess_image_for_ocr(image_bytes: bytes) -> np.ndarray:
    """
    Aplica filtro, binarização e conversão para OpenCV
    """
    try:
        image = Image.open(BytesIO(image_bytes)).convert("L")  # escala de cinza
        image = image.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)
        
        opencv_image = np.array(image)
        _, binary_image = cv2.threshold(opencv_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary_image
    except Exception as e:
        logger.error(f"Erro ao processar imagem para OCR: {str(e)}")
        return None


def extract_text_from_image(image_array: np.ndarray) -> str:
    """
    Aplica OCR com Tesseract em uma imagem OpenCV
    """
    try:
        config = r'--psm 6'
        text = pytesseract.image_to_string(image_array, config=config)
        return text.strip()
    except Exception as e:
        logger.error(f"Erro ao extrair texto da imagem: {str(e)}")
        return ""


def extract_first_integer(text: str) -> int:
    """
    Extrai o primeiro inteiro do texto lido, usado para buscar ID de equipamento
    """
    try:
        for word in text.split():
            if word.isdigit():
                return int(word)
    except Exception as e:
        logger.warning(f"Erro ao extrair inteiro do texto OCR: {str(e)}")
    return None


# Função completa de OCR

def ocr_extract_equipamento_id(image_bytes: bytes) -> int:
    processed_image = preprocess_image_for_ocr(image_bytes)
    if processed_image is not None:
        text = extract_text_from_image(processed_image)
        logger.info(f"Texto extraído do OCR: {text}")
        return extract_first_integer(text)
    return None

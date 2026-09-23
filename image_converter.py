import cv2
import numpy as np
from PIL import Image


def _copy_exif_metadata(source: Image.Image, target: Image.Image) -> Image.Image:
    """변환 과정에서 EXIF가 사라지지 않도록 보존합니다."""
    try:
        exif = source.getexif()
        if exif:
            target.info["exif"] = exif.tobytes()
    except Exception:
        pass
    return target


def _resize_with_opencv(image: Image.Image, max_size: int = 660) -> Image.Image:
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image.copy()

    scale = min(max_size / width, max_size / height)
    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))

    arr = np.asarray(image)
    if image.mode == "RGBA":
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
    elif image.mode == "RGB":
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    elif image.mode == "L":
        bgr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    elif image.mode == "P":
        bgr = np.asarray(image.convert("RGBA"))
        bgr = cv2.cvtColor(bgr, cv2.COLOR_RGBA2BGRA)
    else:
        bgr = np.asarray(image.convert("RGBA"))
        bgr = cv2.cvtColor(bgr, cv2.COLOR_RGBA2BGRA)

    resized = cv2.resize(bgr, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)

    if resized.shape[2] == 4:
        rgba = cv2.cvtColor(resized, cv2.COLOR_BGRA2RGBA)
        return Image.fromarray(rgba, mode="RGBA")

    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb, mode="RGB")


def convert_to_png(
    image: Image.Image,
    max_size: int = 660,
):
    """PIL 이미지 객체를 PNG 형태로 표준화하고 크기를 조절한 새 이미지 객체를 반환합니다."""
    if not isinstance(image, Image.Image):
        raise TypeError("convert_to_png는 PIL Image.Image 객체를 받아야 합니다.")

    resized_image = _resize_with_opencv(image, max_size=max_size)
    if resized_image.mode not in {"RGBA", "LA", "P"}:
        resized_image = resized_image.convert("RGBA")
    resized_image = _copy_exif_metadata(image, resized_image)
    return resized_image.copy()


def convert_to_jpg(
    image: Image.Image,
    max_size: int = 660,
):
    """PIL 이미지 객체를 JPG로 변환한 새 이미지 객체를 반환합니다."""
    if not isinstance(image, Image.Image):
        raise TypeError("convert_to_jpg는 PIL Image.Image 객체를 받아야 합니다.")

    resized_image = _resize_with_opencv(image, max_size=max_size)
    if resized_image.mode not in {"RGBA", "LA", "P"}:
        resized_image = resized_image.convert("RGBA")
    resized_image = _copy_exif_metadata(image, resized_image)
    rgb_image = resized_image.convert("RGB")
    return rgb_image

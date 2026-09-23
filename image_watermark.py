from PIL import Image, ImageDraw, ImageFont

# LENS_TAGS = {
#     0xFDE8: "LensModel",
#     0xFDE9: "LensMake",
#     0xFDEA: "LensSerialNumber",
#     0xC5E0: "LensSpecification",
# }


def _get_exif_value(exif, tag_id):
    value = exif.get(tag_id)
    return value if value not in (None, "") else None


def _format_exposure_text(image: Image.Image):
    exif = image.getexif()
    focal_length = _get_exif_value(exif, 0x920A)
    f_number = _get_exif_value(exif, 0x829D)
    exposure_time = _get_exif_value(exif, 0x829A)
    shutter_speed = _get_exif_value(exif, 0x9201)
    iso_value = _get_exif_value(exif, 0x8827)

    parts = []
    if focal_length is not None:
        parts.append(f"{float(focal_length):g}mm")
    if f_number is not None:
        parts.append(f"f/{float(f_number):g}")

    shutter_value = exposure_time if exposure_time is not None else shutter_speed
    if shutter_value is not None:
        if isinstance(shutter_value, tuple) and len(shutter_value) == 2:
            numerator, denominator = shutter_value
            shutter_text = f"{numerator}/{denominator}s" if denominator else str(shutter_value)
        else:
            shutter_text = str(shutter_value)
            if shutter_text.startswith("0") and "/" in shutter_text:
                shutter_text = shutter_text.lstrip("0")
        parts.append(shutter_text)

    if iso_value is not None:
        iso_text = int(iso_value) if isinstance(iso_value, (int, float)) else str(iso_value)
        parts.append(f"ISO{iso_text}")

    return " ".join(parts) if parts else None


def _get_camera_text(image: Image.Image):
    exif = image.getexif()
    make = _get_exif_value(exif, 0x010F)
    model = _get_exif_value(exif, 0x0110)
    if make and model:
        return f"{make} {model}"
    if make:
        return str(make)
    if model:
        return str(model)
    return None


def _format_lens_value(tag_id, value):
    if value is None:
        return None

    if tag_id == 0xC5E0 and isinstance(value, (tuple, list)) and len(value) >= 4:
        min_focal, max_focal, min_aperture, max_aperture = value[:4]
        min_focal_text = f"{float(min_focal):g}" if isinstance(min_focal, (int, float)) else str(min_focal)
        max_focal_text = f"{float(max_focal):g}" if isinstance(max_focal, (int, float)) else str(max_focal)
        min_ap_text = f"{float(min_aperture):g}" if isinstance(min_aperture, (int, float)) else str(min_aperture)
        max_ap_text = f"{float(max_aperture):g}" if isinstance(max_aperture, (int, float)) else str(max_aperture)
        return f"{min_focal_text}-{max_focal_text}mm f/{min_ap_text}-{max_ap_text}"

    if isinstance(value, (int, float)):
        return f"{float(value):g}"

    if isinstance(value, tuple):
        return " ".join(_format_lens_value(tag_id, item) for item in value if _format_lens_value(tag_id, item))

    return str(value)


def _get_lens_text(image: Image.Image):
    exif = image.getexif()
    lens = _get_exif_value(exif, 0xFDEA)
    if lens:
        return str(lens)
    return None


def build_watermark_text(image: Image.Image, user_text: str):
    lines = []

    camera_text = _get_camera_text(image)
    lens_text = _get_lens_text(image)
    exposure_text = _format_exposure_text(image)

    metadata_parts = []
    if camera_text:
        metadata_parts.append(camera_text)
    if lens_text:
        metadata_parts.append(lens_text)
    if exposure_text:
        metadata_parts.append(exposure_text)

    if metadata_parts:
        lines.append(" ".join(metadata_parts))

    if user_text:
        lines.append(str(user_text))

    return "\n".join(lines)


def get_watermark_style(max_size: int, base_font_size: int = 16, base_margin: int = 10):
    """max_size 기준으로 워터마크 크기와 여백을 비례 계산합니다. max_size=1200일 때 기본값을 적용합니다."""
    if max_size <= 0:
        raise ValueError("max_size는 0보다 커야 합니다.")

    scale = max_size / 1200.0
    font_size = max(18, int(round(base_font_size * scale)))
    margin = max(13, int(round(base_margin * scale)))
    return font_size, margin


def apply_watermark_to_image(
    image: Image.Image,
    watermark_text: str,
    position: str = "right",
    font_size: int = 16,
    color: tuple = (230, 230, 230, 60),
    margin: int = 10,
):
    text = build_watermark_text(image, watermark_text)
    if not text:
        return image

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    working = image.copy()
    draw = ImageDraw.Draw(working)
    try:
        font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    lines = text.splitlines()
    if not lines:
        return image

    line_heights = []
    max_line_width = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        max_line_width = max(max_line_width, line_width)
        line_heights.append(line_height)

    total_text_height = sum(line_heights) + max(0, len(lines) - 1) * 4
    width, height = working.size

    if position in {"right", "bottom_right", "top_right"}:
        anchor_x = width - margin
    elif position in {"bottom_left", "top_left"}:
        anchor_x = margin
    else:
        anchor_x = width - margin

    if position == "right":
        base_y = height - margin - total_text_height
    elif position == "right_center":
        base_y = max(0, (height - total_text_height) // 2)
    elif position == "bottom_right":
        base_y = height - margin - total_text_height
    elif position == "bottom_left":
        base_y = height - margin - total_text_height
    elif position == "top_right":
        base_y = margin
    elif position == "top_left":
        base_y = margin
    else:
        base_y = height - margin - total_text_height

    y_cursor = base_y
    for idx, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = anchor_x - line_width
        if position in {"bottom_left", "top_left"}:
            x = margin
        draw.text((x, y_cursor), line, font=font, fill=color)
        y_cursor += line_heights[idx] + 4

    return working


def add_watermark(
    image: Image.Image,
    watermark_text: str,
    position: str = "right",
    font_size: int = 16,
    color: tuple = (230, 230, 230, 170),
    margin: int = 10,
):
    """PIL 이미지 객체에 워터마크를 추가한 새 이미지 객체를 반환합니다."""
    if not isinstance(image, Image.Image):
        raise TypeError("add_watermark는 PIL Image.Image 객체를 받아야 합니다.")

    image_copy = image.copy()
    return apply_watermark_to_image(image_copy, watermark_text, position, font_size, color, margin)

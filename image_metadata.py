from PIL import Image


# EXIF에서 렌즈 정보에 해당하는 표준 태그만 선택합니다.
LENS_TAGS = {
    0xFDE8,  # LensModel
    0xFDE9,  # LensMake
    0xFDEA,  # LensSerialNumber
    0xC5E0,  # LensSpecification
}


def _build_lens_only_exif(image: Image.Image):
    """기존 EXIF에서 렌즈 관련 태그만 추려 새 EXIF 객체를 생성합니다."""
    exif = image.getexif()
    lens_exif = Image.Exif()

    for tag_id, value in exif.items():
        if tag_id in LENS_TAGS:
            lens_exif[tag_id] = value

    return lens_exif


def _strip_lens_metadata_from_image(image: Image.Image):
    """PIL 이미지 객체에서 EXIF를 제거하고 렌즈 관련 태그만 남긴 새 이미지 객체를 반환합니다."""
    image_data = image.copy()
    image_data.info.clear()

    lens_exif = _build_lens_only_exif(image)
    if lens_exif:
        image_data.info["exif"] = lens_exif.tobytes()

    return image_data


def keep_lens_metadata_only(image: Image.Image):
    """PIL 이미지 객체를 받아 EXIF를 제거하고, 표준 렌즈 태그만 남긴 새 이미지 객체를 반환합니다."""
    if not isinstance(image, Image.Image):
        raise TypeError("keep_lens_metadata_only는 PIL Image.Image 객체만 받습니다.")

    image_data = _strip_lens_metadata_from_image(image)
    return image_data


def strip_all_metadata_keep_lens_only(image: Image.Image):
    """호환성을 위해 표준 이름으로도 제공하는 래퍼 함수입니다."""
    return keep_lens_metadata_only(image)

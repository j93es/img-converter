from PIL import Image


# EXIF에서 카메라 정보에 해당하는 표준 태그만 선택합니다.
CAMERA_TAGS = {
    0x920A,
    0x829D,
    0x829A,
    0x9201,
    0x8827,
    0x0110,
    0xFDEA,
}

def get_striped_metadata_remain_camera(image: Image.Image):
    """PIL 이미지 객체를 받아 EXIF를 제거하고, 표준 렌즈 태그만 남긴 새 이미지 객체를 반환합니다."""
    if not isinstance(image, Image.Image):
        raise TypeError("keep_lens_metadata_only는 PIL Image.Image 객체만 받습니다.")

    """PIL 이미지 객체에서 EXIF를 제거합니다."""
    image_data = image.copy()
    image_data.info.clear()

    """기존 EXIF에서 렌즈 관련 태그만 추려 새 EXIF 객체를 생성합니다."""
    exif = image.getexif()
    target_exif = Image.Exif()
    for tag_id, value in exif.items():
        if tag_id in CAMERA_TAGS:
            target_exif[tag_id] = value

    return target_exif.tobytes()

from pathlib import Path
from typing import List, Union

from PIL import Image

from image_converter import convert_to_jpg, convert_to_png
from image_metadata import strip_all_metadata_keep_lens_only
from image_watermark import add_watermark, get_watermark_style


def list_image_files(folder_path: Union[str, Path], extensions=None) -> List[Path]:
    """폴더 안의 이미지 파일 경로를 모두 리스트로 반환합니다."""
    if extensions is None:
        extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}

    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder}")
    if not folder.is_dir():
        raise ValueError(f"폴더 경로가 아닙니다: {folder}")

    files = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in extensions:
            files.append(path)
    return files


def process_image(image_path, output_path=None, convert_jpg=False, max_size=660, watermark_text=None, keep_lens_only=False):
    input_path = Path(image_path)
    if not input_path.exists():
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"이미지 경로가 아닙니다: {input_path}")

    output_file = Path(output_path) if output_path else input_path.with_name(f"processed{input_path.suffix}")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(input_path) as source_image:
        working = source_image.copy()
        working = convert_to_png(working, max_size=max_size)

        if keep_lens_only:
            working = strip_all_metadata_keep_lens_only(working)

        if watermark_text:
            font_size, margin = get_watermark_style(max_size)
            working = add_watermark(working, watermark_text, font_size=font_size, margin=margin)

            if output_file.suffix.lower() in {".jpg", ".jpeg"}:
                output_file = output_file.with_suffix(".png")

        if convert_jpg and not watermark_text:
            working = convert_to_jpg(working, max_size=max_size)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        working.save(output_file)

    return output_file


def process_folder(folder_path, output_dir="result", convert_jpg=False, max_size=660, watermark_text=None, keep_lens_only=False):
    source_dir = Path(folder_path)
    if not source_dir.exists():
        raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {source_dir}")
    if not source_dir.is_dir():
        raise ValueError(f"폴더 경로가 아닙니다: {source_dir}")

    files = list_image_files(source_dir)
    if not files:
        raise ValueError(f"이미지 파일이 없습니다: {source_dir}")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for image_file in files:
        suffix = ".jpg" if convert_jpg else image_file.suffix.lower() or ".jpg"
        output_path = out_dir / f"{image_file.stem}_processed{suffix}"
        result = process_image(
            image_file,
            output_path=output_path,
            convert_jpg=convert_jpg,
            max_size=max_size,
            watermark_text=watermark_text,
            keep_lens_only=keep_lens_only,
        )
        results.append(result)

    return results

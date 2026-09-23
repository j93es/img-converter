import argparse

from image_batch import process_folder


def build_parser():
    parser = argparse.ArgumentParser(description="폴더 안의 모든 이미지를 처리합니다.")
    parser.add_argument("folder_path", help="이미지 폴더 경로")
    parser.add_argument("-o", "--output", default="result", help="결과 저장 폴더 (기본값: result)")
    parser.add_argument("--convert", action="store_true", help="이미지를 JPG로 변환합니다")
    parser.add_argument("--max-size", type=int, default=660, help="이미지 최대 가로/세로 크기 (기본: 660)")
    parser.add_argument("--watermark", default=None, help="우하단에 삽입할 워터마크 문자열")
    parser.add_argument("--strip-lens-meta", action="store_true", help="렌즈 메타태그만 남기고 나머지 EXIF를 제거합니다")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        results = process_folder(
            args.folder_path,
            output_dir=args.output,
            convert_jpg=args.convert,
            max_size=args.max_size,
            watermark_text=args.watermark,
            keep_lens_only=args.strip_lens_meta,
        )
        print(f"처리 완료: {len(results)}개 파일")
        for path in results:
            print(path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"오류: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

# 사용법

## Init

```sh
git clone https://github.com/j93es/img-converter.git
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
```

## Use

1. 가상 환경 세팅

```sh
source .venv/bin/activate
```

2. 이미지 파일 세팅

./images 폴더 내에 변환을 원하는 이미지 넣기

- input: jpg, png, webp 지원
- output: png, webp 지원

3. 실행

```sh
python main.py ./images -o ./results --max-size 1200 --watermark "abc"
```

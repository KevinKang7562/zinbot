# zinbot

React + Python(FastAPI) 통합 사내 챗봇 프로젝트입니다.

## 기능

- 채팅 화면
  - Enter: 줄바꿈
  - Ctrl+Enter: 전송
  - 보내기 버튼 전송
- 관리자메뉴(좌측 슬라이드)
  - 텍스트 직접 임베딩
  - 파일 임베딩(`.txt/.md/.pdf/.pptx/.png/.jpg/.jpeg/.bmp/.tiff`)
  - 임베딩 리스트 조회(Qdrant)
- 임베딩/검색/응답
  - 임베딩 모델: `text-embedding-multilingual-e5-base`
  - LLM 모델: `gemma-3-1b-it`
  - 벡터DB: Qdrant(`company_docs`)
  - 검색 score `0.80` 이상만 근거로 사용
  - 근거 없으면 LLM 직접 답변

## 프로젝트 구조

```txt
zinbot/
  backend/
    app/
      main.py
      routers/
      services/
  frontend/
    src/
```

## 실행 방법

1) 백엔드 준비

```powershell
cd e:\dev\react\zinbot\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) 환경변수 설정

```powershell
cd e:\dev\react\zinbot
Copy-Item .env.example backend\.env
```

3) 프론트 준비

```powershell
cd e:\dev\react\zinbot\frontend
npm install
```

4) 개발 실행(터미널 2개)

- 터미널 A

```powershell
cd e:\dev\react\zinbot\backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

- 터미널 B

```powershell
cd e:\dev\react\zinbot\frontend
npm run dev
```

브라우저: `http://localhost:5173`

## 통합 배포 실행(백엔드가 프론트 정적 파일 서빙)

```powershell
cd e:\dev\react\zinbot\frontend
npm run build

cd e:\dev\react\zinbot\backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

브라우저: `http://localhost:8000`

## 참고

- LLM/임베딩 API 서버: `http://localhost:1234`
- Qdrant API 서버: `http://localhost:6333`
- 이미지 OCR은 `pytesseract`를 사용하므로 OS에 Tesseract 설치가 필요합니다.
# zinbot

# TIF to PPTX Factory

FastAPI 백엔드와 Vite/Vue3 프론트엔드로 구성된 tif 이미지 기반 PPTX 생성 웹앱입니다.

## Backend

```powershell
cd outputs/backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

MySQL을 사용할 때는 `outputs/docker-compose.yml`로 DB를 띄우고 `.env`의 `DATABASE_URL`을 유지하면 됩니다.
로컬 데모만 빠르게 실행할 경우 `.env` 없이 SQLite 개발 DB가 자동으로 만들어집니다.

## Frontend

```powershell
cd outputs/frontend
npm install
npm run dev -- --port 5173
```

PPTX 실제 생성 로직은 `outputs/backend/app/pptx_generator.py`의 `create_mock_pptx` 함수를 교체하면 됩니다.

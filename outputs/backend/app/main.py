import os
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import Base, STORAGE_DIR, engine, get_db
from .models import PptJob
from .pptx_generator import create_mock_pptx
from .schemas import JobResponse

app = FastAPI(title="TIF to PPTX Factory", version="0.1.0")

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5173,http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/jobs", response_model=JobResponse)
async def create_job(
    request_number: str = Form(...),
    sample_number: str = Form(...),
    tif_files: list[UploadFile] = File(...),
    xlsx_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> JobResponse:
    request_number = request_number.strip()
    sample_number = sample_number.strip()
    if not request_number or not sample_number:
        raise HTTPException(status_code=400, detail="의뢰번호와 시료번호를 모두 입력해 주세요.")

    if not tif_files:
        raise HTTPException(status_code=400, detail="최소 1개 이상의 tif 이미지를 업로드해 주세요.")

    for upload in tif_files:
        if not _has_extension(upload.filename, {".tif", ".tiff"}):
            raise HTTPException(status_code=400, detail="tif 또는 tiff 파일만 이미지로 업로드할 수 있습니다.")

    if xlsx_file and xlsx_file.filename and not _has_extension(xlsx_file.filename, {".xlsx"}):
        raise HTTPException(status_code=400, detail="xlsx 파일만 첨부할 수 있습니다.")

    combined_key = f"{request_number}_{sample_number}"
    job_dir = STORAGE_DIR / "jobs" / uuid4().hex
    image_dir = job_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    image_paths: list[Path] = []
    for upload in tif_files:
        destination = image_dir / f"{uuid4().hex}{Path(upload.filename or 'image.tif').suffix.lower()}"
        await _save_upload(upload, destination)
        image_paths.append(destination)

    saved_xlsx_path: Path | None = None
    if xlsx_file and xlsx_file.filename:
        saved_xlsx_path = job_dir / f"source_{uuid4().hex}.xlsx"
        await _save_upload(xlsx_file, saved_xlsx_path)

    pptx_path = job_dir / f"{_safe_filename(combined_key)}.pptx"

    job = PptJob(
        request_number=request_number,
        sample_number=sample_number,
        combined_key=combined_key,
        status="processing",
        image_count=len(image_paths),
        xlsx_path=str(saved_xlsx_path) if saved_xlsx_path else None,
        original_xlsx_name=xlsx_file.filename if xlsx_file and xlsx_file.filename else None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        create_mock_pptx(
            output_path=pptx_path,
            combined_key=combined_key,
            image_paths=image_paths,
            xlsx_path=saved_xlsx_path,
        )
        job.pptx_path = str(pptx_path)
        job.status = "complete"
    except Exception as exc:
        job.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"PPTX 생성 중 오류가 발생했습니다: {exc}") from exc

    db.commit()
    db.refresh(job)
    return _to_response(job)


@app.get("/api/jobs", response_model=list[JobResponse])
def search_jobs(query: str = "", db: Session = Depends(get_db)) -> list[JobResponse]:
    statement = db.query(PptJob)
    normalized = query.strip()
    if normalized:
        like = f"%{normalized}%"
        statement = statement.filter(
            or_(
                PptJob.combined_key.ilike(like),
                PptJob.request_number.ilike(like),
                PptJob.sample_number.ilike(like),
            )
        )

    jobs = statement.order_by(PptJob.created_at.desc()).limit(40).all()
    return [_to_response(job) for job in jobs]


@app.get("/api/jobs/{job_id}/download/pptx")
def download_pptx(job_id: int, db: Session = Depends(get_db)) -> FileResponse:
    job = _get_job(db, job_id)
    if not job.pptx_path:
        raise HTTPException(status_code=404, detail="PPTX 파일이 아직 생성되지 않았습니다.")

    path = Path(job.pptx_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="PPTX 파일을 찾을 수 없습니다.")

    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"{_safe_filename(job.combined_key)}.pptx",
    )


@app.get("/api/jobs/{job_id}/download/xlsx")
def download_xlsx(job_id: int, db: Session = Depends(get_db)) -> FileResponse:
    job = _get_job(db, job_id)
    if not job.xlsx_path:
        raise HTTPException(status_code=404, detail="업로드된 XLSX 파일이 없습니다.")

    path = Path(job.xlsx_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="XLSX 파일을 찾을 수 없습니다.")

    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=job.original_xlsx_name or f"{_safe_filename(job.combined_key)}.xlsx",
    )


def _get_job(db: Session, job_id: int) -> PptJob:
    job = db.get(PptJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    return job


async def _save_upload(upload: UploadFile, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as file:
        while chunk := await upload.read(1024 * 1024):
            file.write(chunk)
    await upload.close()


def _has_extension(filename: str | None, allowed: set[str]) -> bool:
    return Path(filename or "").suffix.lower() in allowed


def _safe_filename(value: str) -> str:
    safe = "".join(character if character.isalnum() or character in ("-", "_") else "_" for character in value)
    return safe[:180] or "pptx_result"


def _to_response(job: PptJob) -> JobResponse:
    return JobResponse(
        id=job.id,
        request_number=job.request_number,
        sample_number=job.sample_number,
        combined_key=job.combined_key,
        status=job.status,
        image_count=job.image_count,
        has_xlsx=bool(job.xlsx_path),
        pptx_download_url=f"/api/jobs/{job.id}/download/pptx" if job.pptx_path else None,
        xlsx_download_url=f"/api/jobs/{job.id}/download/xlsx" if job.xlsx_path else None,
        created_at=job.created_at,
    )

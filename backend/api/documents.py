
import uuid

from pathlib import Path

from fastapi import (
    APIRouter, Depends, UploadFile,
    File, HTTPException
)

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.database.connection import get_db

from backend.database.repositories import (
    CaseRepository,
    DocumentRepository
)

from backend.api.auth import get_current_user
from backend.rag.ingestion import ingestion_service

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = settings.database_path / "data" / "raw"


@router.post("/upload/{case_id}")
async def upload_document(
    case_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    case = CaseRepository(db).get(case_id)

    if not case or case.created_by != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Case not found."
        )

    extension = Path(
        file.filename or ""
    ).suffix.lower().lstrip(".")

    if extension not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file extension."
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_filename = f"{uuid.uuid4()}.{extension}"

    destination = UPLOAD_DIR / safe_filename

    size = 0
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    try:

        with destination.open("wb") as output:

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                size += len(chunk)

                if size > max_size:
                    raise HTTPException(
                        status_code=413,
                        detail="File size exceeds the upload limit."
                    )

                output.write(chunk)

        result = ingestion_service.ingest(
            str(destination)
        )

        document = DocumentRepository(db).create(
            case_id=case_id,
            filename=file.filename,
            file_path=str(destination),
            file_type=extension,
            checksum=result["checksum"],
            processing_status="completed",
            metadata_json=result
        )

        return {
            "success": True,
            "message": "Document uploaded and indexed.",
            "data": {
                "document_id": document.id,
                "filename": document.filename,
                "chunks_created": result["chunks_created"],
                "processing_status": document.processing_status
            }
        }

    except HTTPException:
        if destination.exists():
            destination.unlink()
        raise

    except Exception:

        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed."
        )

    finally:
        await file.close()

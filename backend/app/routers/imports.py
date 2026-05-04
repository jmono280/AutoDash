from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.imports import ImportResultOut
from app.services.import_service import ImportService

router = APIRouter()


def _service() -> ImportService:
    return ImportService()


def _assert_pdf(file: UploadFile) -> None:
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF (.pdf)",
        )


def _assert_xlsx(file: UploadFile) -> None:
    if not (file.filename or "").lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel workbook (.xlsx)",
        )


def _parse_error(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Could not parse file: {exc}",
    )


@router.post("/daily-sales", response_model=ImportResultOut, status_code=status.HTTP_201_CREATED)
async def import_daily_sales(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    service: ImportService = Depends(_service),
    _: User = Depends(get_current_user),
) -> ImportResultOut:
    _assert_pdf(file)
    try:
        return await service.import_daily_sales(db, await file.read())
    except (ValueError, Exception) as exc:
        raise _parse_error(exc) from exc


@router.post("/hours-summary", response_model=ImportResultOut, status_code=status.HTTP_201_CREATED)
async def import_hours_summary(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    service: ImportService = Depends(_service),
    _: User = Depends(get_current_user),
) -> ImportResultOut:
    _assert_pdf(file)
    try:
        return await service.import_hours_summary(db, await file.read())
    except (ValueError, Exception) as exc:
        raise _parse_error(exc) from exc


@router.post("/hours-detail", response_model=ImportResultOut, status_code=status.HTTP_201_CREATED)
async def import_hours_detail(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    service: ImportService = Depends(_service),
    _: User = Depends(get_current_user),
) -> ImportResultOut:
    _assert_pdf(file)
    try:
        return await service.import_hours_detail(db, await file.read())
    except (ValueError, Exception) as exc:
        raise _parse_error(exc) from exc


@router.post("/work-in-progress", response_model=ImportResultOut, status_code=status.HTTP_201_CREATED)
async def import_wip(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    service: ImportService = Depends(_service),
    _: User = Depends(get_current_user),
) -> ImportResultOut:
    _assert_xlsx(file)
    try:
        return await service.import_wip(db, await file.read())
    except (ValueError, Exception) as exc:
        raise _parse_error(exc) from exc

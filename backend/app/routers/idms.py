from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.idms import (
    IdmsChargeOffKpisOut,
    IdmsChargeOffMonthlyDetailOut,
    IdmsChargeOffMonthlyOut,
    IdmsChargeOffOut,
    IdmsChargeOffOverviewOut,
    IdmsSalesBySalespersonOut,
    IdmsSalesByVehicleOut,
    IdmsSalesKpisOut,
    IdmsSalesMonthlyOut,
    IdmsSalesOut,
    IdmsSessionStatusOut,
    IdmsSyncOut,
)
from app.services.idms_service import IdmsService

router = APIRouter()


class OtpPayload(BaseModel):
    otp_code: str | None = None


def _service() -> IdmsService:
    return IdmsService()


@router.get("/session", response_model=IdmsSessionStatusOut)
async def session_status(
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsSessionStatusOut:
    data = service.check_session()
    return IdmsSessionStatusOut(**data)


@router.post("/login", response_model=IdmsSessionStatusOut)
async def login(
    body: OtpPayload,
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsSessionStatusOut:
    data = service.login(otp_code=body.otp_code)
    return IdmsSessionStatusOut(**data)


@router.post("/charge-offs/sync", response_model=IdmsSyncOut)
async def sync_charge_offs(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsSyncOut:
    return await service.sync_charge_offs(db, year=year)


@router.post(
    "/charge-offs/import-historical",
    response_model=IdmsSyncOut,
    status_code=status.HTTP_201_CREATED,
)
async def import_charge_off_historical(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsSyncOut:
    if not (file.filename or "").lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un Excel (.xlsx o .xls)",
        )
    try:
        return await service.import_charge_off_historical(db, await file.read())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo parsear el archivo: {exc}",
        )


@router.get("/charge-offs", response_model=list[IdmsChargeOffOut])
async def list_charge_offs(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[IdmsChargeOffOut]:
    rows = await service.get_charge_offs(db, year=year)
    return [IdmsChargeOffOut.model_validate(r) for r in rows]


@router.get("/charge-offs/kpis", response_model=IdmsChargeOffKpisOut)
async def get_charge_off_kpis(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsChargeOffKpisOut:
    data = await service.get_charge_off_kpis(db, year=year)
    return IdmsChargeOffKpisOut(**data)


@router.get("/charge-offs/monthly", response_model=list[IdmsChargeOffMonthlyOut])
async def get_charge_off_monthly(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[IdmsChargeOffMonthlyOut]:
    rows = await service.get_charge_off_monthly(db, year=year)
    return [IdmsChargeOffMonthlyOut(**r) for r in rows]


@router.get("/charge-offs/years", response_model=list[int])
async def get_charge_off_years(
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[int]:
    return await service.get_available_years(db)


@router.get("/charge-offs/overview", response_model=IdmsChargeOffOverviewOut)
async def get_charge_off_overview(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsChargeOffOverviewOut:
    data = await service.get_charge_off_overview(db, year=year)
    return IdmsChargeOffOverviewOut(**data)


@router.get(
    "/charge-offs/monthly-detail", response_model=list[IdmsChargeOffMonthlyDetailOut]
)
async def get_charge_off_monthly_detail(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[IdmsChargeOffMonthlyDetailOut]:
    rows = await service.get_charge_off_monthly_detail(db, year=year)
    return [IdmsChargeOffMonthlyDetailOut(**r) for r in rows]


@router.post("/month-end/sync", response_model=IdmsSyncOut)
async def sync_month_end(
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsSyncOut:
    return await service.sync_month_end(db)


# ------------------------------------------------------------------
# Sales
# ------------------------------------------------------------------


@router.post("/sales/sync", response_model=IdmsSyncOut)
async def sync_sales(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsSyncOut:
    return await service.sync_sales(db, year=year)


@router.post(
    "/sales/import-historical",
    response_model=IdmsSyncOut,
    status_code=status.HTTP_201_CREATED,
)
async def import_sales_historical(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsSyncOut:
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un CSV (.csv)",
        )
    try:
        return await service.import_sales_historical(db, await file.read())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo parsear el archivo: {exc}",
        )


@router.get("/sales", response_model=list[IdmsSalesOut])
async def list_sales(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[IdmsSalesOut]:
    rows = await service.get_sales(db, year=year)
    return [IdmsSalesOut.model_validate(r) for r in rows]


@router.get("/sales/kpis", response_model=IdmsSalesKpisOut)
async def get_sales_kpis(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> IdmsSalesKpisOut:
    data = await service.get_sales_kpis(db, year=year)
    return IdmsSalesKpisOut(**data)


@router.get("/sales/monthly", response_model=list[IdmsSalesMonthlyOut])
async def get_sales_monthly(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[IdmsSalesMonthlyOut]:
    rows = await service.get_sales_monthly(db, year=year)
    return [IdmsSalesMonthlyOut(**r) for r in rows]


@router.get("/sales/years", response_model=list[int])
async def get_sales_years(
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[int]:
    return await service.get_sales_years(db)


@router.get("/sales/by-salesperson", response_model=list[IdmsSalesBySalespersonOut])
async def get_sales_by_salesperson(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[IdmsSalesBySalespersonOut]:
    rows = await service.get_sales_by_salesperson(db, year=year)
    return [IdmsSalesBySalespersonOut(**r) for r in rows]


@router.get("/sales/by-vehicle", response_model=list[IdmsSalesByVehicleOut])
async def get_sales_by_vehicle(
    year: int,
    db: AsyncSession = Depends(get_db),
    service: IdmsService = Depends(_service),
    _: User = Depends(get_current_user),
) -> list[IdmsSalesByVehicleOut]:
    rows = await service.get_sales_by_vehicle(db, year=year)
    return [IdmsSalesByVehicleOut(**r) for r in rows]

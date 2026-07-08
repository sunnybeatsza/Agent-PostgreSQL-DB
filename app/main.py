from contextlib import asynccontextmanager
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, check_database_connection, engine, get_db
from app.models import (
    ConsumerAlert,
    ConsumerMeterData,
    ConsumerProfile,
    ConsumerReport,
    GovernmentReport,
    GovMeterData,
    TechnicianData,
)
from app.schemas import (
    ConsumerAlertCreate,
    ConsumerAlertRead,
    ConsumerAlertUpdate,
    ConsumerMeterDataCreate,
    ConsumerMeterDataRead,
    ConsumerMeterDataUpdate,
    ConsumerProfileCreate,
    ConsumerProfileRead,
    ConsumerProfileUpdate,
    ConsumerReportCreate,
    ConsumerReportRead,
    ConsumerReportUpdate,
    DatabaseHealthRead,
    GovernmentReportCreate,
    GovernmentReportRead,
    GovernmentReportUpdate,
    GovMeterDataCreate,
    GovMeterDataRead,
    GovMeterDataUpdate,
    HealthRead,
    TechnicianDataCreate,
    TechnicianDataRead,
    TechnicianDataUpdate,
)

settings = get_settings()
ModelT = TypeVar("ModelT", bound=Base)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


def create_crud_router(
    *,
    model: type[ModelT],
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
    prefix: str,
    tags: list[str],
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)
    model_name = model.__name__

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def create_record(payload: create_schema, db: Session = Depends(get_db)) -> ModelT:  # type: ignore[valid-type]
        record = model(**payload.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @router.get("", response_model=list[read_schema])
    def list_records(
        db: Session = Depends(get_db),
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[ModelT]:
        statement = select(model).order_by(model.id).limit(limit).offset(offset)
        return list(db.scalars(statement).all())

    @router.get("/{record_id}", response_model=read_schema)
    def get_record(record_id: int, db: Session = Depends(get_db)) -> ModelT:
        record = db.get(model, record_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model_name} not found")
        return record

    @router.patch("/{record_id}", response_model=read_schema)
    def update_record(record_id: int, payload: update_schema, db: Session = Depends(get_db)) -> ModelT:  # type: ignore[valid-type]
        record = db.get(model, record_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model_name} not found")

        updates: dict[str, Any] = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(record, field, value)

        db.commit()
        db.refresh(record)
        return record

    @router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_record(record_id: int, db: Session = Depends(get_db)) -> None:
        record = db.get(model, record_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model_name} not found")

        db.delete(record)
        db.commit()

    return router


@app.get("/health", response_model=HealthRead, tags=["health"])
def health() -> HealthRead:
    return HealthRead(status="ok")


@app.get("/health/db", response_model=DatabaseHealthRead, tags=["health"])
def database_health() -> DatabaseHealthRead:
    try:
        check_database_connection()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from exc
    return DatabaseHealthRead(status="ok", database="connected")


app.include_router(
    create_crud_router(
        model=ConsumerProfile,
        create_schema=ConsumerProfileCreate,
        update_schema=ConsumerProfileUpdate,
        read_schema=ConsumerProfileRead,
        prefix="/consumer-profiles",
        tags=["consumer agent"],
    )
)
app.include_router(
    create_crud_router(
        model=ConsumerMeterData,
        create_schema=ConsumerMeterDataCreate,
        update_schema=ConsumerMeterDataUpdate,
        read_schema=ConsumerMeterDataRead,
        prefix="/consumer-meter-data",
        tags=["consumer agent"],
    )
)
app.include_router(
    create_crud_router(
        model=ConsumerReport,
        create_schema=ConsumerReportCreate,
        update_schema=ConsumerReportUpdate,
        read_schema=ConsumerReportRead,
        prefix="/consumer-reports",
        tags=["consumer agent"],
    )
)
app.include_router(
    create_crud_router(
        model=ConsumerAlert,
        create_schema=ConsumerAlertCreate,
        update_schema=ConsumerAlertUpdate,
        read_schema=ConsumerAlertRead,
        prefix="/consumer-alerts",
        tags=["consumer agent"],
    )
)
app.include_router(
    create_crud_router(
        model=GovMeterData,
        create_schema=GovMeterDataCreate,
        update_schema=GovMeterDataUpdate,
        read_schema=GovMeterDataRead,
        prefix="/gov-meter-data",
        tags=["government agent"],
    )
)
app.include_router(
    create_crud_router(
        model=GovernmentReport,
        create_schema=GovernmentReportCreate,
        update_schema=GovernmentReportUpdate,
        read_schema=GovernmentReportRead,
        prefix="/government-reports",
        tags=["government agent"],
    )
)
app.include_router(
    create_crud_router(
        model=TechnicianData,
        create_schema=TechnicianDataCreate,
        update_schema=TechnicianDataUpdate,
        read_schema=TechnicianDataRead,
        prefix="/technicians-data",
        tags=["government agent"],
    )
)

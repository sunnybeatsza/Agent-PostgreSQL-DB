from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ConsumerProfile(TimestampMixin, Base):
    __tablename__ = "consumer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    meter_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    household_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class ConsumerMeterData(TimestampMixin, Base):
    __tablename__ = "consumer_meter_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    consumer_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("consumer_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    meter_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    reading_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    energy_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    voltage: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_amp: Mapped[float | None] = mapped_column(Float, nullable=True)
    power_kw: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class ConsumerReport(TimestampMixin, Base):
    __tablename__ = "consumer_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    consumer_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("consumer_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    meter_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    generated_by: Mapped[str] = mapped_column(String(100), default="consumer_agent", nullable=False)


class ConsumerAlert(TimestampMixin, Base):
    __tablename__ = "consumer_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    consumer_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("consumer_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    meter_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False, index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class GovMeterData(TimestampMixin, Base):
    __tablename__ = "gov_meter_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meter_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    municipality: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    reading_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    energy_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    outage_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    grid_health_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class GovernmentReport(TimestampMixin, Base):
    __tablename__ = "government_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    municipality: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    findings: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    generated_by: Mapped[str] = mapped_column(String(100), default="government_agent", nullable=False)


class TechnicianData(TimestampMixin, Base):
    __tablename__ = "technicians_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    technician_name: Mapped[str] = mapped_column(String(255), nullable=False)
    technician_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    specialty: Mapped[str | None] = mapped_column(String(150), nullable=True)
    availability_status: Mapped[str] = mapped_column(String(50), default="available", nullable=False, index=True)
    assigned_meter_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

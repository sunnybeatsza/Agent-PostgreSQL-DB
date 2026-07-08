from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthRead(BaseModel):
    status: str


class DatabaseHealthRead(HealthRead):
    database: str


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Timestamps(BaseModel):
    created_at: datetime
    updated_at: datetime


class ConsumerProfileBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    phone_number: str | None = Field(default=None, max_length=50)
    address: str | None = None
    meter_id: str = Field(min_length=1, max_length=100)
    household_size: int | None = Field(default=None, ge=1)
    metadata_json: dict[str, Any] | None = None


class ConsumerProfileCreate(ConsumerProfileBase):
    pass


class ConsumerProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, min_length=3, max_length=255)
    phone_number: str | None = Field(default=None, max_length=50)
    address: str | None = None
    meter_id: str | None = Field(default=None, min_length=1, max_length=100)
    household_size: int | None = Field(default=None, ge=1)
    metadata_json: dict[str, Any] | None = None


class ConsumerProfileRead(ConsumerProfileBase, Timestamps, OrmModel):
    id: int


class ConsumerMeterDataBase(BaseModel):
    consumer_profile_id: int | None = None
    meter_id: str = Field(min_length=1, max_length=100)
    reading_timestamp: datetime
    energy_kwh: float = Field(ge=0)
    voltage: float | None = None
    current_amp: float | None = None
    power_kw: float | None = None
    raw_payload: dict[str, Any] | None = None


class ConsumerMeterDataCreate(ConsumerMeterDataBase):
    pass


class ConsumerMeterDataUpdate(BaseModel):
    consumer_profile_id: int | None = None
    meter_id: str | None = Field(default=None, min_length=1, max_length=100)
    reading_timestamp: datetime | None = None
    energy_kwh: float | None = Field(default=None, ge=0)
    voltage: float | None = None
    current_amp: float | None = None
    power_kw: float | None = None
    raw_payload: dict[str, Any] | None = None


class ConsumerMeterDataRead(ConsumerMeterDataBase, Timestamps, OrmModel):
    id: int


class ConsumerReportBase(BaseModel):
    consumer_profile_id: int | None = None
    meter_id: str = Field(min_length=1, max_length=100)
    report_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(min_length=1)
    recommendations: dict[str, Any] | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    generated_by: str = Field(default="consumer_agent", max_length=100)


class ConsumerReportCreate(ConsumerReportBase):
    pass


class ConsumerReportUpdate(BaseModel):
    consumer_profile_id: int | None = None
    meter_id: str | None = Field(default=None, min_length=1, max_length=100)
    report_type: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = Field(default=None, min_length=1)
    recommendations: dict[str, Any] | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    generated_by: str | None = Field(default=None, max_length=100)


class ConsumerReportRead(ConsumerReportBase, Timestamps, OrmModel):
    id: int


class ConsumerAlertBase(BaseModel):
    consumer_profile_id: int | None = None
    meter_id: str = Field(min_length=1, max_length=100)
    severity: str = Field(min_length=1, max_length=50)
    alert_type: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1)
    status: str = Field(default="open", max_length=50)
    detected_at: datetime
    resolved_at: datetime | None = None
    details: dict[str, Any] | None = None


class ConsumerAlertCreate(ConsumerAlertBase):
    pass


class ConsumerAlertUpdate(BaseModel):
    consumer_profile_id: int | None = None
    meter_id: str | None = Field(default=None, min_length=1, max_length=100)
    severity: str | None = Field(default=None, min_length=1, max_length=50)
    alert_type: str | None = Field(default=None, min_length=1, max_length=100)
    message: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, max_length=50)
    detected_at: datetime | None = None
    resolved_at: datetime | None = None
    details: dict[str, Any] | None = None


class ConsumerAlertRead(ConsumerAlertBase, Timestamps, OrmModel):
    id: int


class GovMeterDataBase(BaseModel):
    meter_id: str = Field(min_length=1, max_length=100)
    region: str = Field(min_length=1, max_length=100)
    municipality: str | None = Field(default=None, max_length=150)
    reading_timestamp: datetime
    energy_kwh: float = Field(ge=0)
    outage_detected: bool = False
    grid_health_score: float | None = Field(default=None, ge=0, le=100)
    raw_payload: dict[str, Any] | None = None


class GovMeterDataCreate(GovMeterDataBase):
    pass


class GovMeterDataUpdate(BaseModel):
    meter_id: str | None = Field(default=None, min_length=1, max_length=100)
    region: str | None = Field(default=None, min_length=1, max_length=100)
    municipality: str | None = Field(default=None, max_length=150)
    reading_timestamp: datetime | None = None
    energy_kwh: float | None = Field(default=None, ge=0)
    outage_detected: bool | None = None
    grid_health_score: float | None = Field(default=None, ge=0, le=100)
    raw_payload: dict[str, Any] | None = None


class GovMeterDataRead(GovMeterDataBase, Timestamps, OrmModel):
    id: int


class GovernmentReportBase(BaseModel):
    region: str = Field(min_length=1, max_length=100)
    municipality: str | None = Field(default=None, max_length=150)
    report_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(min_length=1)
    findings: dict[str, Any] | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    generated_by: str = Field(default="government_agent", max_length=100)


class GovernmentReportCreate(GovernmentReportBase):
    pass


class GovernmentReportUpdate(BaseModel):
    region: str | None = Field(default=None, min_length=1, max_length=100)
    municipality: str | None = Field(default=None, max_length=150)
    report_type: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = Field(default=None, min_length=1)
    findings: dict[str, Any] | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    generated_by: str | None = Field(default=None, max_length=100)


class GovernmentReportRead(GovernmentReportBase, Timestamps, OrmModel):
    id: int


class TechnicianDataBase(BaseModel):
    technician_name: str = Field(min_length=1, max_length=255)
    technician_email: str | None = Field(default=None, min_length=3, max_length=255)
    phone_number: str | None = Field(default=None, max_length=50)
    region: str = Field(min_length=1, max_length=100)
    specialty: str | None = Field(default=None, max_length=150)
    availability_status: str = Field(default="available", max_length=50)
    assigned_meter_id: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class TechnicianDataCreate(TechnicianDataBase):
    pass


class TechnicianDataUpdate(BaseModel):
    technician_name: str | None = Field(default=None, min_length=1, max_length=255)
    technician_email: str | None = Field(default=None, min_length=3, max_length=255)
    phone_number: str | None = Field(default=None, max_length=50)
    region: str | None = Field(default=None, min_length=1, max_length=100)
    specialty: str | None = Field(default=None, max_length=150)
    availability_status: str | None = Field(default=None, max_length=50)
    assigned_meter_id: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class TechnicianDataRead(TechnicianDataBase, Timestamps, OrmModel):
    id: int

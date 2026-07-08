from datetime import UTC, datetime, timedelta

from sqlalchemy import delete

try:
    from _path import add_project_root_to_path
except ModuleNotFoundError:
    from scripts._path import add_project_root_to_path

add_project_root_to_path()

from app.database import Base, SessionLocal, engine
from app.models import (
    ConsumerAlert,
    ConsumerMeterData,
    ConsumerProfile,
    ConsumerReport,
    GovernmentReport,
    GovMeterData,
    TechnicianData,
)

SEED_GENERATOR = "seed_script"
SEED_METER_PATTERN = "SEED-MTR-%"
SEED_EMAIL_PATTERNS = ("seed.%@example.test", "seed.%@example.com")


def delete_existing_seed_data(db) -> None:
    statements = [
        delete(ConsumerAlert).where(ConsumerAlert.meter_id.like(SEED_METER_PATTERN)),
        delete(ConsumerReport).where(ConsumerReport.generated_by == SEED_GENERATOR),
        delete(ConsumerMeterData).where(ConsumerMeterData.meter_id.like(SEED_METER_PATTERN)),
        delete(GovMeterData).where(GovMeterData.meter_id.like(SEED_METER_PATTERN)),
        delete(GovernmentReport).where(GovernmentReport.generated_by == SEED_GENERATOR),
        delete(TechnicianData).where(
            TechnicianData.technician_email.like(SEED_EMAIL_PATTERNS[0])
            | TechnicianData.technician_email.like(SEED_EMAIL_PATTERNS[1])
        ),
        delete(ConsumerProfile).where(
            ConsumerProfile.email.like(SEED_EMAIL_PATTERNS[0])
            | ConsumerProfile.email.like(SEED_EMAIL_PATTERNS[1])
        ),
    ]
    for statement in statements:
        db.execute(statement)


def appliance_profile(profile_index: int, hour: int) -> tuple[list[dict], list[dict]]:
    base_profiles = [
        {
            "fridge": [0.18, 0.19, 0.2, 0.19, 0.18, 0.2],
            "geyser": [0.2, 0.25, 0.35, 1.4, 1.7, 1.2],
            "kettle": [0.0, 0.0, 0.0, 0.32, 0.0, 0.0],
            "washing_machine": [0.0, 0.0, 0.55, 0.35, 0.0, 0.0],
            "lighting": [0.1, 0.12, 0.16, 0.26, 0.32, 0.35],
            "entertainment": [0.08, 0.1, 0.12, 0.18, 0.28, 0.3],
        },
        {
            "fridge": [0.16, 0.16, 0.17, 0.16, 0.17, 0.16],
            "geyser": [0.15, 0.2, 0.25, 0.35, 0.25, 0.2],
            "stove": [0.0, 0.0, 0.0, 0.5, 1.4, 0.3],
            "microwave": [0.0, 0.0, 0.0, 0.18, 0.22, 0.0],
            "lighting": [0.08, 0.1, 0.13, 0.2, 0.28, 0.3],
            "computer": [0.22, 0.2, 0.18, 0.16, 0.14, 0.12],
        },
        {
            "fridge": [0.22, 0.24, 0.7, 0.82, 0.88, 0.74],
            "geyser": [0.22, 0.28, 0.35, 0.45, 0.3, 0.25],
            "pool_pump": [0.0, 0.0, 0.0, 0.95, 1.05, 0.0],
            "washing_machine": [0.0, 0.6, 0.45, 0.0, 0.0, 0.0],
            "lighting": [0.12, 0.14, 0.18, 0.28, 0.35, 0.36],
            "security_system": [0.08, 0.08, 0.08, 0.08, 0.08, 0.08],
        },
    ]

    profile = base_profiles[profile_index]
    anomalies: list[dict] = []

    if profile_index == 0 and hour in {4, 5}:
        profile["geyser"][hour] = 3.4
        anomalies.append(
            {
                "type": "geyser_stuck_on",
                "appliance": "geyser",
                "severity": "high",
                "description": "Geyser draw stayed above expected heating cycle threshold.",
            }
        )

    if profile_index == 1 and hour == 4:
        profile["stove"][hour] = 3.1
        anomalies.append(
            {
                "type": "cooking_load_spike",
                "appliance": "stove",
                "severity": "medium",
                "description": "Short high-load stove event above household baseline.",
            }
        )

    if profile_index == 2 and hour in {2, 3, 4}:
        anomalies.append(
            {
                "type": "fridge_continuous_draw",
                "appliance": "fridge",
                "severity": "high",
                "description": "Fridge compressor appears to run continuously across multiple intervals.",
            }
        )

    appliances = [
        {
            "name": appliance,
            "energy_kwh": round(values[hour], 2),
            "confidence": 0.91 if appliance in {"fridge", "geyser", "lighting"} else 0.84,
        }
        for appliance, values in profile.items()
    ]
    return appliances, anomalies


def main() -> int:
    Base.metadata.create_all(bind=engine)

    now = datetime.now(UTC).replace(microsecond=0)
    with SessionLocal() as db:
        delete_existing_seed_data(db)

        profiles = [
            ConsumerProfile(
                full_name="Seed Consumer Alice Mokoena",
                email="seed.alice@example.com",
                phone_number="+27110000001",
                address="12 Meter Street, Johannesburg",
                meter_id="SEED-MTR-1001",
                household_size=4,
                metadata_json={
                    "seeded": True,
                    "tariff_plan": "residential_peak",
                    "profiled_appliances": ["fridge", "geyser", "kettle", "washing_machine", "lighting", "entertainment"],
                },
            ),
            ConsumerProfile(
                full_name="Seed Consumer Brian Naidoo",
                email="seed.brian@example.com",
                phone_number="+27110000002",
                address="45 Grid Avenue, Pretoria",
                meter_id="SEED-MTR-1002",
                household_size=2,
                metadata_json={
                    "seeded": True,
                    "tariff_plan": "residential_standard",
                    "profiled_appliances": ["fridge", "geyser", "stove", "microwave", "lighting", "computer"],
                },
            ),
            ConsumerProfile(
                full_name="Seed Consumer Clara Dlamini",
                email="seed.clara@example.com",
                phone_number="+27110000003",
                address="8 Appliance Lane, Soweto",
                meter_id="SEED-MTR-1003",
                household_size=5,
                metadata_json={
                    "seeded": True,
                    "tariff_plan": "residential_standard",
                    "profiled_appliances": ["fridge", "geyser", "pool_pump", "washing_machine", "lighting", "security_system"],
                },
            ),
        ]
        db.add_all(profiles)
        db.flush()

        meter_rows: list[ConsumerMeterData] = []
        gov_meter_rows: list[GovMeterData] = []
        for profile_index, profile in enumerate(profiles):
            for hour in range(6):
                reading_time = now - timedelta(hours=6 - hour)
                appliances, anomalies = appliance_profile(profile_index, hour)
                energy = round(sum(item["energy_kwh"] for item in appliances), 2)
                voltage = 229.0 + hour * 0.35
                outage_detected = False

                if profile_index == 2 and hour == 4:
                    voltage = 198.5
                    outage_detected = True
                    anomalies.append(
                        {
                            "type": "voltage_sag",
                            "appliance": None,
                            "severity": "high",
                            "description": "Supply voltage dropped below safe operating range.",
                        }
                    )

                raw_payload = {
                    "seeded": True,
                    "source": "seed_db.py",
                    "interval_minutes": 60,
                    "meter_capability": "appliance_load_disaggregation",
                    "appliance_breakdown": appliances,
                    "anomalies": anomalies,
                }

                meter_rows.append(
                    ConsumerMeterData(
                        consumer_profile_id=profile.id,
                        meter_id=profile.meter_id,
                        reading_timestamp=reading_time,
                        energy_kwh=energy,
                        voltage=round(voltage, 2),
                        current_amp=round((energy * 1000) / max(voltage, 1), 2),
                        power_kw=round(energy, 2),
                        raw_payload=raw_payload,
                    )
                )
                gov_meter_rows.append(
                    GovMeterData(
                        meter_id=profile.meter_id,
                        region="Gauteng",
                        municipality="Johannesburg" if profile_index != 1 else "Tshwane",
                        reading_timestamp=reading_time,
                        energy_kwh=energy,
                        outage_detected=outage_detected,
                        grid_health_score=round(95 - profile_index * 2 - hour * 0.7 - (12 if outage_detected else 0), 2),
                        raw_payload={
                            "seeded": True,
                            "source": "seed_db.py",
                            "consumer_anomaly_count": len(anomalies),
                            "anomaly_types": [item["type"] for item in anomalies],
                        },
                    )
                )

        db.add_all(meter_rows)
        db.add_all(gov_meter_rows)

        db.add_all(
            [
                ConsumerReport(
                    consumer_profile_id=profiles[0].id,
                    meter_id=profiles[0].meter_id,
                    report_type="appliance_profile",
                    title="Seed Appliance Usage Profile",
                    summary="The geyser dominates evening consumption and shows a stuck-on signature in the latest intervals.",
                    recommendations={
                        "seeded": True,
                        "actions": ["Inspect geyser thermostat", "Set geyser timer to avoid extended evening heating"],
                        "detected_anomalies": ["geyser_stuck_on"],
                    },
                    period_start=now - timedelta(hours=6),
                    period_end=now,
                    generated_by=SEED_GENERATOR,
                ),
                ConsumerReport(
                    consumer_profile_id=profiles[2].id,
                    meter_id=profiles[2].meter_id,
                    report_type="appliance_anomaly",
                    title="Seed Fridge Continuous Draw Report",
                    summary="The fridge load profile indicates sustained compressor operation across multiple readings.",
                    recommendations={
                        "seeded": True,
                        "actions": ["Check fridge door seal", "Inspect thermostat or compressor", "Move heat sources away from fridge"],
                        "detected_anomalies": ["fridge_continuous_draw", "voltage_sag"],
                    },
                    period_start=now - timedelta(hours=6),
                    period_end=now,
                    generated_by=SEED_GENERATOR,
                ),
                ConsumerAlert(
                    consumer_profile_id=profiles[0].id,
                    meter_id=profiles[0].meter_id,
                    severity="high",
                    alert_type="geyser_stuck_on",
                    message="Seed alert: geyser power draw stayed unusually high across consecutive intervals.",
                    status="open",
                    detected_at=now - timedelta(hours=1),
                    details={"seeded": True, "appliance": "geyser", "expected_kwh": 1.2, "observed_kwh": 3.4},
                ),
                ConsumerAlert(
                    consumer_profile_id=profiles[1].id,
                    meter_id=profiles[1].meter_id,
                    severity="medium",
                    alert_type="cooking_load_spike",
                    message="Seed alert: stove load spiked above normal household cooking baseline.",
                    status="open",
                    detected_at=now - timedelta(hours=2),
                    details={"seeded": True, "appliance": "stove", "baseline_kwh": 1.4, "observed_kwh": 3.1},
                ),
                ConsumerAlert(
                    consumer_profile_id=profiles[2].id,
                    meter_id=profiles[2].meter_id,
                    severity="high",
                    alert_type="fridge_continuous_draw",
                    message="Seed alert: fridge compressor appears to be running continuously.",
                    status="investigating",
                    detected_at=now - timedelta(hours=3),
                    details={"seeded": True, "appliance": "fridge", "duration_intervals": 3},
                ),
                ConsumerAlert(
                    consumer_profile_id=profiles[2].id,
                    meter_id=profiles[2].meter_id,
                    severity="high",
                    alert_type="voltage_sag",
                    message="Seed alert: meter detected a voltage sag during the appliance profiling window.",
                    status="investigating",
                    detected_at=now - timedelta(hours=2),
                    details={"seeded": True, "observed_voltage": 198.5, "threshold_voltage": 207.0},
                ),
                GovernmentReport(
                    region="Gauteng",
                    municipality="Johannesburg",
                    report_type="smart_meter_anomaly_summary",
                    title="Seed Regional Smart Meter Anomaly Summary",
                    summary="Seeded smart meter data includes appliance-level anomalies and one localized voltage sag signal.",
                    findings={
                        "seeded": True,
                        "meters_observed": 3,
                        "anomaly_types": ["geyser_stuck_on", "cooking_load_spike", "fridge_continuous_draw", "voltage_sag"],
                        "recommended_dispatch_meter_ids": ["SEED-MTR-1001", "SEED-MTR-1003"],
                    },
                    period_start=now - timedelta(hours=6),
                    period_end=now,
                    generated_by=SEED_GENERATOR,
                ),
                TechnicianData(
                    technician_name="Seed Technician Naledi Khumalo",
                    technician_email="seed.tech.naledi@example.com",
                    phone_number="+27110000100",
                    region="Gauteng",
                    specialty="Smart meter and appliance diagnostics",
                    availability_status="available",
                    assigned_meter_id="SEED-MTR-1003",
                    notes="Seeded technician available to inspect fridge continuous draw and voltage sag.",
                ),
                TechnicianData(
                    technician_name="Seed Technician Sipho Maseko",
                    technician_email="seed.tech.sipho@example.com",
                    phone_number="+27110000101",
                    region="Gauteng",
                    specialty="Geyser and high-load appliance diagnostics",
                    availability_status="assigned",
                    assigned_meter_id="SEED-MTR-1001",
                    notes="Seeded technician assigned to geyser stuck-on anomaly.",
                ),
            ]
        )

        db.commit()

    print("Seed data inserted successfully.")
    print("Created appliance-profiled smart meter readings with geyser, stove, fridge, and voltage anomalies.")
    print("Run `python scripts/cleanup_seed_data.py` to remove this seeded data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

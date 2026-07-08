from sqlalchemy import delete

try:
    from _path import add_project_root_to_path
except ModuleNotFoundError:
    from scripts._path import add_project_root_to_path

add_project_root_to_path()

from app.database import SessionLocal
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


def main() -> int:
    with SessionLocal() as db:
        counts: dict[str, int] = {}

        statements = [
            ("consumer_alerts", delete(ConsumerAlert).where(ConsumerAlert.meter_id.like(SEED_METER_PATTERN))),
            ("consumer_reports", delete(ConsumerReport).where(ConsumerReport.generated_by == SEED_GENERATOR)),
            ("consumer_meter_data", delete(ConsumerMeterData).where(ConsumerMeterData.meter_id.like(SEED_METER_PATTERN))),
            ("gov_meter_data", delete(GovMeterData).where(GovMeterData.meter_id.like(SEED_METER_PATTERN))),
            ("government_reports", delete(GovernmentReport).where(GovernmentReport.generated_by == SEED_GENERATOR)),
            (
                "technicians_data",
                delete(TechnicianData).where(
                    TechnicianData.technician_email.like(SEED_EMAIL_PATTERNS[0])
                    | TechnicianData.technician_email.like(SEED_EMAIL_PATTERNS[1])
                ),
            ),
            (
                "consumer_profiles",
                delete(ConsumerProfile).where(
                    ConsumerProfile.email.like(SEED_EMAIL_PATTERNS[0])
                    | ConsumerProfile.email.like(SEED_EMAIL_PATTERNS[1])
                ),
            ),
        ]

        for name, statement in statements:
            result = db.execute(statement)
            counts[name] = result.rowcount or 0

        db.commit()

    print("Seed data cleanup completed.")
    for table_name, count in counts.items():
        print(f"{table_name}: deleted {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

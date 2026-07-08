from datetime import UTC, datetime


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_consumer_profile_crud(client):
    create_response = client.post(
        "/consumer-profiles",
        json={
            "full_name": "Test Consumer",
            "email": "test.consumer@example.com",
            "meter_id": "TEST-MTR-1",
            "household_size": 3,
            "metadata_json": {"profiled_appliances": ["fridge", "geyser"]},
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] == 1
    assert created["email"] == "test.consumer@example.com"

    list_response = client.get("/consumer-profiles")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        "/consumer-profiles/1",
        json={"household_size": 4},
    )
    assert update_response.status_code == 200
    assert update_response.json()["household_size"] == 4

    delete_response = client.delete("/consumer-profiles/1")
    assert delete_response.status_code == 204

    missing_response = client.get("/consumer-profiles/1")
    assert missing_response.status_code == 404


def test_consumer_meter_data_accepts_appliance_payload_and_anomalies(client):
    reading_time = datetime(2026, 7, 9, 12, 0, tzinfo=UTC).isoformat()

    response = client.post(
        "/consumer-meter-data",
        json={
            "meter_id": "TEST-MTR-2",
            "reading_timestamp": reading_time,
            "energy_kwh": 4.2,
            "voltage": 198.5,
            "current_amp": 21.1,
            "power_kw": 4.2,
            "raw_payload": {
                "meter_capability": "appliance_load_disaggregation",
                "appliance_breakdown": [
                    {"name": "fridge", "energy_kwh": 0.88, "confidence": 0.91},
                    {"name": "geyser", "energy_kwh": 3.4, "confidence": 0.91},
                ],
                "anomalies": [
                    {
                        "type": "geyser_stuck_on",
                        "appliance": "geyser",
                        "severity": "high",
                    }
                ],
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()["raw_payload"]
    assert payload["meter_capability"] == "appliance_load_disaggregation"
    assert payload["anomalies"][0]["type"] == "geyser_stuck_on"


def test_unknown_record_returns_404(client):
    response = client.get("/government-reports/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "GovernmentReport not found"

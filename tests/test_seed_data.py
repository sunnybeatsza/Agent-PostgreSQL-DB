from scripts.seed_db import appliance_profile


def test_seed_profile_includes_geyser_stuck_on_anomaly():
    appliances, anomalies = appliance_profile(profile_index=0, hour=4)

    geyser = next(item for item in appliances if item["name"] == "geyser")
    assert geyser["energy_kwh"] == 3.4
    assert any(item["type"] == "geyser_stuck_on" for item in anomalies)


def test_seed_profile_includes_fridge_continuous_draw_anomaly():
    appliances, anomalies = appliance_profile(profile_index=2, hour=3)

    fridge = next(item for item in appliances if item["name"] == "fridge")
    assert fridge["energy_kwh"] == 0.82
    assert any(item["type"] == "fridge_continuous_draw" for item in anomalies)

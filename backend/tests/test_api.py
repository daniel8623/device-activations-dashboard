def test_new_device_is_created(client):
    response = client.post("/api/activations", json={"device_id": "device-1"})

    assert response.status_code == 201
    assert response.json()["is_new"] is True


def test_duplicate_ping_is_not_counted_twice(client):
    first = client.post(
        "/api/activations",
        json={"device_id": "device-1", "activated_at": "2026-03-01T10:00:00Z"},
    )
    second = client.post(
        "/api/activations",
        json={"device_id": "device-1", "activated_at": "2026-05-01T10:00:00Z"},
    )

    assert second.status_code == 200
    assert second.json()["is_new"] is False
    # The original activation time is kept.
    assert second.json()["activated_at"] == first.json()["activated_at"]


def test_empty_device_id_is_rejected(client):
    response = client.post("/api/activations", json={"device_id": ""})

    assert response.status_code == 422


def test_activation_time_is_stored_in_utc(client):
    # 01:30 in Israel (UTC+2) on Jan 1 is 23:30 UTC on Dec 31.
    response = client.post(
        "/api/activations",
        json={"device_id": "device-1", "activated_at": "2026-01-01T01:30:00+02:00"},
    )

    assert response.json()["activated_at"] == "2025-12-31T23:30:00"


def test_timeseries_rejects_unknown_granularity(client):
    response = client.get("/api/stats/timeseries", params={"granularity": "year"})

    assert response.status_code == 422


def test_timeseries_returns_requested_number_of_points(client):
    response = client.get("/api/stats/timeseries", params={"granularity": "month", "buckets": 12})

    assert response.status_code == 200
    assert len(response.json()["points"]) == 12
import pytest

pytestmark = pytest.mark.integration


def test_create_job(client):
    response = client.post("/jobs", json={"topic": "Por que o céu é azul"})
    assert response.status_code == 201
    data = response.json()
    assert data["topic"] == "Por que o céu é azul"
    assert data["status"] == "pending"
    assert data["error"] is None
    assert "id" in data


def test_create_job_rejects_short_topic(client):
    response = client.post("/jobs", json={"topic": "ab"})
    assert response.status_code == 422


def test_get_job(client):
    created = client.post("/jobs", json={"topic": "Como funcionam os relâmpagos"}).json()
    response = client.get(f"/jobs/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_job_not_found(client):
    response = client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_list_jobs(client):
    client.post("/jobs", json={"topic": "Primeiro tema curioso"})
    client.post("/jobs", json={"topic": "Segundo tema curioso"})
    response = client.get("/jobs")
    assert response.status_code == 200
    assert len(response.json()) >= 2
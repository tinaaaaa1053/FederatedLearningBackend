"""
API endpoint tests
"""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "FederatedLearningBackend"


def test_dashboard_stats(client: TestClient):
    """Test dashboard stats endpoint"""
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["code"] == 200
    assert "data" in data


def test_job_list(client: TestClient):
    """Test job list endpoint"""
    response = client.post("/api/job/list", json={
        "pageNo": 1,
        "pageSize": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["code"] == 200


def test_client_list(client: TestClient):
    """Test client list endpoint"""
    response = client.post("/api/client/list", json={
        "pageNo": 1,
        "pageSize": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["code"] == 200


def test_model_list(client: TestClient):
    """Test model list endpoint"""
    response = client.post("/api/model/list", json={
        "pageNo": 1,
        "pageSize": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["code"] == 200


def test_settings_get(client: TestClient):
    """Test settings get endpoint"""
    response = client.get("/api/settings/get")
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["code"] == 200


def test_data_quality_stats(client: TestClient):
    """Test data quality stats endpoint"""
    response = client.get("/api/dataQuality/stats")
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["code"] == 200

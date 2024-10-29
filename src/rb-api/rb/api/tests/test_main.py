from fastapi.testclient import TestClient
from rb.api.main import app

client = TestClient(app)


def test_liveness():
    response = client.get("/probes/liveness/")
    assert response.status_code == 200
    assert response.json() == {"message": "RescueBox API"}

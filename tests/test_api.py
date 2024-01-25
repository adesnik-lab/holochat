import time

import pytest
from fastapi.testclient import TestClient

from holochat.main import app
from holochat.settings import load_settings

pytestmark = pytest.mark.api

client = TestClient(app)

settings = load_settings()
TIME_TO_STALE = settings.message_stale_secs
TIME_TO_EXPIRE = settings.message_expire_secs

@pytest.fixture(autouse=True)
def setup_db():
    client.delete("/db")
    yield
    client.delete("/db")

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to HoloChat!"}
    
def test_post_message():
    response = client.post("/msg/pc", json={"message": "Holography is fun."})
    assert response.status_code == 200
    assert response.json() == {"message": "Message received.", "target": "pc"}
    
def test_message_freshness():
    response = client.post("/msg/pc", json={"message": "Test freshness"})
    time.sleep(0.1)
    response = client.get("/msg/pc")
    assert response.status_code == 200
    assert response.json()["message_freshness"] == "fresh"

@pytest.mark.slow
def test_message_staleness():
    response = client.post("/msg/pc", json={"message": "Test staleness"})
    time.sleep(TIME_TO_STALE)
    response = client.get("/msg/pc")
    assert response.status_code == 200
    assert response.json()["message_freshness"] == "stale"

@pytest.mark.slow    
def test_message_expiration():
    response = client.post("/msg/pc", json={"message": "Test expiration"})
    time.sleep(TIME_TO_EXPIRE)
    response = client.get("/msg/pc")
    assert response.status_code == 200
    assert response.json()["message_freshness"] == "expired"
    
def test_mesage_ages():
    client.post("/msg/pc", json={"message": "Test age"})
    time.sleep(0.1)
    response = client.get("/msg/pc")
    t1 = response.json()["message_age_secs"]
    time.sleep(0.1)
    response = client.get("/msg/pc")
    t2 = response.json()["message_age_secs"]
    assert t2 > t1
    
def test_message_read_increment():
    response = client.post("/msg/pc", json={'message': 'test increment'})
    r1 = client.get("/msg/pc")
    j1 = r1.json()
    time.sleep(0.1)
    r2 = client.get("/msg/pc")
    j2 = r2.json()
    assert response.status_code == 200
    assert j1["read_count"] == 0
    assert j2["read_count"] == 1

def test_message_status():
    response = client.post("/msg/pc", json={'message': 'test status'})
    r1 = client.get("/msg/pc")
    j1 = r1.json()
    time.sleep(0.1)
    r2 = client.get("/msg/pc")
    j2 = r2.json()
    assert response.status_code == 200
    assert j1["message_status"] == "new"
    assert j2["message_status"] == "read"
    
def test_message_is_read():
    response = client.post("/msg/pc", json={'message': 'test status'})
    response = client.get("/msg/pc")
    # read it again to increment read_count and change status
    response = client.get("/msg/pc")
    assert response.status_code == 200
    assert response.json()["message_status"] == "read"
    
def test_message_overwrites():
    response = client.post("/msg/pc", json={'message': 'test overwrite'})
    r1 = client.get("/msg/pc")
    j1 = r1.json()
    time.sleep(0.1)
    response = client.post("/msg/pc", json={'message': 'test overwrite again'})
    r2 = client.get("/msg/pc")
    j2 = r2.json()
    assert response.status_code == 200
    assert j1["message"] == "test overwrite"
    assert j2["message"] == "test overwrite again"
    assert j1["recv_time"] != j2["recv_time"]
    assert j1["request_time"] != j2["request_time"]
    assert j1["message"] != j2["message"]
    
def test_delete_message():
    response = client.post("/msg/pc", json={'message': 'test delete'})
    assert response.status_code == 200
    response = client.delete("/msg/pc")
    response = client.get("/msg/pc")
    assert response.status_code == 404
    
def test_delete_all_messages():
    response = client.post("/msg/pc", json={'message': 'test delete'})
    response = client.post("/msg/pc2", json={'message': 'test delete'})
    response = client.post("/msg/pc3", json={'message': 'test delete'})
    assert response.status_code == 200
    response = client.delete("/msg")
    assert response.status_code == 200
    response = client.get("/msg/pc")
    assert response.status_code == 404
    response = client.get("/msg/pc2")
    assert response.status_code == 404
    response = client.get("/msg/pc3")
    assert response.status_code == 404

def test_message_count_increment():
    n_posts = 5
    for _ in range(n_posts):
        response = client.post("/msg/pc1", json={'message': 'test count'})
    response = client.get("/db/pc1")
    assert response.json()["message_count"] == n_posts
    
def test_config_post():
    response = client.post("/config/pc1", json={"test": "config"})
    assert response.status_code == 200
    assert response.json() == {"message": "Config received.", "target": "pc1"}
    
def test_config_get():
    response = client.post("/config/pc1", json={"test": "config"})
    response = client.get("/config/pc1")
    assert response.status_code == 200
    assert response.json() == {"test": "config"}
    
def test_config_delete():
    response = client.post("/config/pc1", json={"test": "config"})
    response = client.delete("/config/pc1")
    assert response.status_code == 200
    assert response.json() == {"message": "Config deleted.", "target": "pc1"}
    response = client.get("/config/pc1")
    assert response.status_code == 404
    
def test_db_model_structure():
    client.post("/msg/pc1", json={"message": "Test db model structure"})
    client.post("/config/pc1", json={"test": "config"})
    response = client.get("/db/pc1")
    assert response.status_code == 200
    assert all(key in response.json() for key in ["messages", "config", "message_count"])
    
def test_db_delete():
    client.post("/msg/pc1", json={"message": "Test db delete"})
    client.post("/config/pc1", json={"test": "config"})
    response = client.delete("/db/pc1")
    assert response.status_code == 200
    response = client.get("/db/pc1")
    assert response.status_code == 404
    
def test_db_delete_all():
    client.post("/msg/pc1", json={"message": "Test full db delete"})
    client.post("/config/pc1", json={"test": "config"})
    client.post("/msg/pc2", json={"message": "Test full db delete"})
    response = client.delete("/db")
    assert response.status_code == 200
    assert response.json() == {"message": "Database deleted."}
    response = client.get("/db/pc1")
    assert response.status_code == 404
    response = client.get("/db/pc2")
    assert response.status_code == 404
    
def test_unknown_sender():
    client.post("/msg/pc1", json={"message": "Test unknown sender"})
    response = client.get("/msg/pc1")
    assert response.status_code == 200
    assert response.json()["sender"] == "unknown"

def test_known_sender():
    client.post("/msg/pc1", json={"message": "Test known sender", "sender": "holo"})
    response = client.get("/msg/pc1")
    assert response.status_code == 200
    assert response.json()["sender"] == "holo"
    
def test_pc_key_exists_in_db():
    response = client.post("/msg/pc1", json={"message": "Test pc key exists"})
    response = client.get("/db/pc1")
    assert response.status_code == 200
    
def test_missing_key_raises_404():
    response = client.get("/db/pc1")
    assert response.status_code == 404
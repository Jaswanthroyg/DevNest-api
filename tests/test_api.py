"""End-to-end test of the main flow. Run with:  pytest"""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"  # use a separate DB for tests

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # 'with' runs startup (creates tables + admin)
        yield c
    os.remove("test.db")


def signup_and_login(client, name):
    client.post("/auth/register", json={"username": name, "email": f"{name}@x.com", "password": "password123"})
    r = client.post("/auth/login", data={"username": f"{name}@x.com", "password": "password123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_full_flow(client):
    asker, helper = signup_and_login(client, "asker"), signup_and_login(client, "helper")

    # Ask a question and answer it
    q = client.post("/questions", json={"title": "What is a decorator?", "body": "Explain Python decorators please"}, headers=asker).json()
    a = client.post(f"/questions/{q['id']}/answers", json={"body": "A function wrapping a function."}, headers=helper).json()

    # Rules: can't vote on own answer; others can; only asker can accept
    assert client.post(f"/answers/{a['id']}/vote", json={"value": 1}, headers=helper).status_code == 400
    assert client.post(f"/answers/{a['id']}/vote", json={"value": 1}, headers=asker).json()["score"] == 1
    assert client.post(f"/answers/{a['id']}/accept", headers=helper).status_code == 403
    assert client.post(f"/answers/{a['id']}/accept", headers=asker).json()["is_accepted"] is True
    assert client.get(f"/questions/{q['id']}").json()["is_answered"] is True

    # Unauthenticated and non-admin access is blocked
    assert client.post("/questions", json={"title": "No token", "body": "Should fail here"}).status_code == 401
    assert client.get("/admin/users", headers=asker).status_code == 403

    # Admin can delete anything
    r = client.post("/auth/login", data={"username": "admin@example.com", "password": "admin12345"})
    admin = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert client.delete(f"/questions/{q['id']}", headers=admin).status_code == 204
    assert client.get(f"/questions/{q['id']}").status_code == 404

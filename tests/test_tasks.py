import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_create_task_success(auth_client):
    with patch("app.api.routes.tasks.run_task") as mock_task:
        response = await auth_client.post("/tasks/", json={
            "name": "Test Task",
            "is_recurring": False,
            "email_to": "receiver@example.com",
            "email_subject": "Test",
            "email_body": "Hello"
        })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_create_task_without_auth(client):
    response = await client.post("/tasks/", json={
        "name": "Test Task",
        "is_recurring": False
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_tasks(auth_client):
    with patch("app.api.routes.tasks.run_task"):
        await auth_client.post("/tasks/", json={
            "name": "Task 1",
            "is_recurring": False
        })
        await auth_client.post("/tasks/", json={
            "name": "Task 2",
            "is_recurring": False
        })
    
    response = await auth_client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2

@pytest.mark.asyncio
async def test_delete_task(auth_client):
    with patch("app.api.routes.tasks.run_task"):
        create_response = await auth_client.post("/tasks/", json={
            "name": "Task to delete",
            "is_recurring": False
        })
    task_id = create_response.json()["id"]
    
    response = await auth_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_cannot_access_other_users_task(client):
    await client.post("/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "pass1234"
    })
    login1 = await client.post("/auth/login", data={
        "username": "user1", "password": "pass1234"
    })
    token1 = login1.json()["access_token"]
    
    with patch("app.api.routes.tasks.run_task"):
        task_response = await client.post(
            "/tasks/",
            json={"name": "Private Task", "is_recurring": False},
            headers={"Authorization": f"Bearer {token1}"}
        )
    task_id = task_response.json()["id"]
    
    await client.post("/auth/register", json={
        "username": "user2",
        "email": "user2@example.com",
        "password": "pass1234"
    })
    login2 = await client.post("/auth/login", data={
        "username": "user2", "password": "pass1234"
    })
    token2 = login2.json()["access_token"]
    
    response = await client.get(
        f"/tasks/{task_id}/runs",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_max_tasks_per_user(auth_client):
    with patch("app.api.routes.tasks.run_task"):
        for i in range(10):
            await auth_client.post("/tasks/", json={
                "name": f"Task {i}",
                "is_recurring": False
            })
        
        response = await auth_client.post("/tasks/", json={
            "name": "Task 11",
            "is_recurring": False
        })
    assert response.status_code == 429
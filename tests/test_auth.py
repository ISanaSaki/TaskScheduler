import pytest

@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    await client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    response = await client.post("/auth/register", json={
        "username": "alice",
        "email": "alice2@example.com",
        "password": "secret123"
    })
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    response = await client.post("/auth/register", json={
        "username": "alice2",
        "email": "alice@example.com",
        "password": "secret123"
    })
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    response = await client.post("/auth/login", data={
        "username": "alice",
        "password": "secret123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    response = await client.post("/auth/login", data={
        "username": "alice",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token(client):
    await client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    login_response = await client.post("/auth/login", data={
        "username": "alice",
        "password": "secret123"
    })
    refresh_token = login_response.json()["refresh_token"]
    
    response = await client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client):
    response = await client.post("/auth/refresh", json={
        "refresh_token": "invalid.token.here"
    })
    assert response.status_code == 401
import pytest
from httpx import AsyncClient
import json
from fastapi import status

from src.main import app
from test.e2e.test_auth import register_test_user, login_test_user


@pytest.fixture
async def test_client():
    """Create a test client for the API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def admin_token(test_client):
    """Get an admin token for testing."""
    # This would typically register and login an admin user
    # For testing purposes, we'll use a mock token
    return "admin_test_token"


@pytest.fixture
async def user_token(test_client):
    """Get a regular user token for testing."""
    # This would typically register and login a regular user
    # For testing purposes, we'll use a mock token
    return "user_test_token"


@pytest.fixture
async def test_user_data():
    """Create test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.mark.asyncio
async def test_register_user(test_client, test_user_data):
    """Test registering a new user."""
    response = await register_test_user(test_client, test_user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert data["user"]["username"] == test_user_data["username"]
    assert data["user"]["email"] == test_user_data["email"]
    assert "password" not in data["user"]


@pytest.mark.asyncio
async def test_login_user(test_client, test_user_data):
    """Test logging in a user."""
    # First register the user
    await register_test_user(test_client, test_user_data)
    
    # Then login
    response = await login_test_user(test_client, test_user_data["username"], test_user_data["password"])
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert data["user"]["username"] == test_user_data["username"]


@pytest.mark.asyncio
async def test_get_current_user(test_client, registered_user):
    """Test getting the current user profile."""
    response = await test_client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == registered_user["user_data"]["username"]
    assert data["email"] == registered_user["user_data"]["email"]


@pytest.mark.asyncio
async def test_reset_password(test_client, registered_user):
    """Test resetting a user's password."""
    reset_data = {
        "current_password": registered_user["user_data"]["password"],
        "new_password": "NewPassword456!"
    }
    
    response = await test_client.post(
        "/api/users/reset-password",
        json=reset_data,
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "success" in data["message"].lower()
    
    # Test login with new password
    response = await login_test_user(
        test_client, 
        registered_user["user_data"]["username"], 
        "NewPassword456!"
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_admin_get_all_users(test_client, registered_admin):
    """Test admin getting all users."""
    response = await test_client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {registered_admin['access_token']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Check that we have at least one user (the one we registered)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_admin_get_user_by_id(test_client, registered_admin, registered_user):
    """Test admin getting a user by ID."""
    response = await test_client.get(
        f"/api/users/{registered_user['user_id']}",
        headers={"Authorization": f"Bearer {registered_admin['access_token']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["_id"] == registered_user["user_id"]


@pytest.mark.asyncio
async def test_admin_delete_user(test_client, registered_admin, registered_user):
    """Test admin deleting a user."""
    response = await test_client.delete(
        f"/api/users/{registered_user['user_id']}",
        headers={"Authorization": f"Bearer {registered_admin['access_token']}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the user is gone
    response = await test_client.get(
        f"/api/users/{registered_user['user_id']}",
        headers={"Authorization": f"Bearer {registered_admin['access_token']}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_non_admin_cannot_get_all_users(test_client, registered_user):
    """Test that non-admin users cannot get all users."""
    response = await test_client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_non_admin_cannot_delete_user(test_client, registered_user, registered_admin):
    """Test that non-admin users cannot delete users."""
    response = await test_client.delete(
        f"/api/users/{registered_admin['user_id']}",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN 
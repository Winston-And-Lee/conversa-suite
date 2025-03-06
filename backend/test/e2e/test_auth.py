"""Test helpers for authentication."""
import pytest
from httpx import AsyncClient
import json
from fastapi import status

from src.main import app


async def register_test_user(client: AsyncClient, user_data: dict):
    """Register a test user and return the response."""
    return await client.post("/api/users/register", json=user_data)


async def login_test_user(client: AsyncClient, username: str, password: str):
    """Login a test user and return the response."""
    login_data = {
        "username": username,
        "password": password
    }
    return await client.post(
        "/api/users/login", 
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )


@pytest.fixture
async def registered_user(test_client):
    """Register a test user and return the user data and token."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = await register_test_user(test_client, user_data)
    data = response.json()
    
    return {
        "user_data": user_data,
        "user_id": data["user"]["_id"],
        "access_token": data["access_token"]
    }


@pytest.fixture
async def registered_admin(test_client):
    """Register a test admin user and return the user data and token."""
    admin_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "first_name": "Admin",
        "last_name": "User"
    }
    
    # Register the admin user
    response = await register_test_user(test_client, admin_data)
    data = response.json()
    user_id = data["user"]["_id"]
    
    # Update the user to be an admin (this would typically be done in the database)
    # For testing purposes, we'll just return a token that we'll mock to have admin privileges
    
    return {
        "user_data": admin_data,
        "user_id": user_id,
        "access_token": data["access_token"]
    } 
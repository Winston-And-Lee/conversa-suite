import pytest
import jwt
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import bcrypt

from src.domain.models.user import User
from src.domain.entity.user_create import UserCreate
from src.usecase.user.user_usecase import UserUsecase


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    repository = MagicMock()
    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.get_by_email = AsyncMock()
    repository.get_by_username = AsyncMock()
    repository.get_all = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()
    repository.verify_password = AsyncMock()
    repository.store_refresh_token = AsyncMock()
    repository.invalidate_refresh_token = AsyncMock()
    return repository


@pytest.fixture
def user_usecase(mock_user_repository):
    """Create a user use case with mock repository."""
    usecase = UserUsecase()
    usecase.user_repository = mock_user_repository
    return usecase


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id="1",
        username="testuser",
        email="test@example.com",
        password_hash="$2b$12$CwY2DJ7LuoOw9AJ1Kz7IB.3VPnxjVdyPkMeWSUyQ1JXFbjkLnKxpS",  # hashed 'password123'
        first_name="Test",
        last_name="User",
    )


@pytest.mark.asyncio
async def test_register_user(user_usecase, mock_user_repository, sample_user):
    """Test registering a user."""
    # Arrange
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.get_by_username.return_value = None
    mock_user_repository.create.return_value = sample_user
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # Act
    with patch.object(jwt, 'encode', return_value="test_token"):
        user, token = await user_usecase.register_user(user_data)
    
    # Assert
    assert user == sample_user
    assert token == "test_token"
    mock_user_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_user_login(user_usecase, mock_user_repository, sample_user):
    """Test user login."""
    # Arrange
    mock_user_repository.get_by_username.return_value = sample_user
    mock_user_repository.store_refresh_token.return_value = True
    
    # Act
    with patch('bcrypt.checkpw', return_value=True), patch.object(jwt, 'encode', return_value="test_token"):
        user, token = await user_usecase.user_login("testuser", "password123")
    
    # Assert
    assert user == sample_user
    assert token == "test_token"
    mock_user_repository.store_refresh_token.assert_called_once()


@pytest.mark.asyncio
async def test_user_authentication(user_usecase, mock_user_repository, sample_user):
    """Test user authentication."""
    # Arrange
    mock_user_repository.get_by_id.return_value = sample_user
    
    # Create a valid token
    payload = {
        "sub": "1",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, user_usecase.jwt_secret_key, algorithm=user_usecase.jwt_algorithm)
    
    # Act
    user = await user_usecase.user_authentication(token)
    
    # Assert
    assert user == sample_user
    mock_user_repository.get_by_id.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_user_request_verification(user_usecase, mock_user_repository, sample_user):
    """Test requesting user verification."""
    # Arrange
    mock_user_repository.get_by_email.return_value = sample_user
    mock_user_repository.update.return_value = sample_user
    
    # Act
    with patch.object(user_usecase, '_send_verification_email', AsyncMock(return_value=True)):
        token = await user_usecase.user_request_verification("test@example.com")
    
    # Assert
    assert token is not None
    mock_user_repository.get_by_email.assert_called_once_with("test@example.com")
    mock_user_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password(user_usecase, mock_user_repository, sample_user):
    """Test resetting a user's password."""
    # Arrange
    mock_user_repository.get_by_id.return_value = sample_user
    mock_user_repository.update.return_value = sample_user
    
    # Act
    with patch('bcrypt.checkpw', return_value=True):
        result = await user_usecase.reset_password("1", "current_password", "new_password")
    
    # Assert
    assert result is True
    mock_user_repository.get_by_id.assert_called_once_with("1")
    mock_user_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_user_logout(user_usecase, mock_user_repository):
    """Test user logout."""
    # Arrange
    mock_user_repository.invalidate_refresh_token.return_value = True
    
    # Act
    result = await user_usecase.user_logout("refresh_token")
    
    # Assert
    assert result is True
    mock_user_repository.invalidate_refresh_token.assert_called_once_with("refresh_token") 
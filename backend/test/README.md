# Testing Guide

This directory contains tests for the Conversa-Suite backend application.

## Test Structure

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for component interactions
- `e2e/`: End-to-end tests for API endpoints

## Running Tests

To run all tests:

```bash
cd backend
pytest
```

To run specific test types:

```bash
# Run unit tests only
pytest test/unit

# Run integration tests only
pytest test/integration

# Run end-to-end tests only
pytest test/e2e
```

To run a specific test file:

```bash
pytest test/e2e/test_user_api.py
```

## Test Database

The tests use a separate MongoDB database (`conversa_test`) to avoid affecting the development or production databases. The test database is automatically set up and torn down during testing.

## Writing Tests

### Unit Tests

Unit tests should test individual components in isolation, using mocks for dependencies.

Example:
```python
@pytest.mark.asyncio
async def test_create_user(user_usecase, mock_user_repository, sample_user):
    # Arrange
    mock_user_repository.create.return_value = sample_user

    # Act
    result = await user_usecase.create_user(sample_user)

    # Assert
    assert result == sample_user
    mock_user_repository.create.assert_called_once_with(sample_user)
```

### End-to-End Tests

End-to-end tests should test the API endpoints from the client's perspective.

Example:
```python
@pytest.mark.asyncio
async def test_register_user(test_client, test_user_data):
    response = await register_test_user(test_client, test_user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "user" in data
    assert "access_token" in data
```

## Test Fixtures

Common test fixtures are defined in:
- `conftest.py`: Global fixtures
- `test/e2e/test_auth.py`: Authentication fixtures
- `test/e2e/test_db.py`: Database fixtures 
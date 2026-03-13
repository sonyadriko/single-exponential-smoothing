import pytest
from services.auth_service import verify_password, get_password_hash, create_access_token, decode_token
from datetime import timedelta


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_and_verify(self):
        """Test that hashed passwords can be verified."""
        password = "test123"
        hashed = get_password_hash(password)

        assert password != hashed
        assert verify_password(password, hashed) is True

    def test_wrong_password(self):
        """Test that wrong passwords are rejected."""
        password = "correct123"
        wrong_password = "wrong123"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_is_unique(self):
        """Test that hashing the same password twice produces different hashes (bcrypt salt)."""
        password = "test123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2


class TestTokenCreation:
    """Test JWT token creation and decoding."""

    def test_create_token(self):
        """Test creating a basic access token."""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)

    def test_create_token_with_expiration(self):
        """Test creating a token with custom expiration."""
        data = {"sub": "testuser", "role": "admin"}
        expires = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires)

        assert token is not None

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["username"] == "testuser"
        assert decoded["role"] == "admin"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        decoded = decode_token(invalid_token)

        assert decoded is None

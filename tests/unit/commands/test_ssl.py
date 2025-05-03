"""Unit tests for SSL command functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from porkbun.commands.ssl import retrieve, generate, ssl
from porkbun.utils.exceptions import PorkbunAPIError

@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()

def test_retrieve_success(runner):
    """Test successful retrieval of SSL certificate"""
    mock_response = {
        "status": "SUCCESS",
        "certificatechain": ["-----BEGIN CERTIFICATE-----\n..."],
        "intermediatecertificate": {
            "type": "Standard",
            "notafter": "2024-12-31 00:00:00"
        },
        "privatekey": "-----BEGIN PRIVATE KEY-----\n...",
        "publickey": "-----BEGIN PUBLIC KEY-----\n..."
    }
    
    with patch('porkbun.commands.ssl.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(ssl, ['retrieve', 'example.com'])
        assert result.exit_code == 0
        mock_request.assert_called_once_with('ssl/retrieve/example.com', {})
        assert "SSL Certificate for example.com" in result.output

def test_retrieve_error(runner):
    """Test error handling when SSL certificate is not found"""
    mock_response = {
        "status": "ERROR",
        "message": "SSL certificate not found"
    }
    
    with patch('porkbun.commands.ssl.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(ssl, ['retrieve', 'example.com'])
        assert result.exit_code == 0  # Command succeeds but shows error message
        mock_request.assert_called_once_with('ssl/retrieve/example.com', {})
        assert "Error retrieving certificate" in result.output

def test_generate_success(runner):
    """Test successful generation of SSL certificate"""
    mock_retrieve_response = {"status": "ERROR", "message": "Certificate not found"}
    mock_generate_response = {
        "status": "SUCCESS",
        "certificatechain": ["-----BEGIN CERTIFICATE-----\n..."],
        "privatekey": "-----BEGIN PRIVATE KEY-----\n..."
    }
    
    # Create a mock that returns different values based on the endpoint
    def side_effect(endpoint, data=None):
        if endpoint == 'ssl/retrieve/example.com':
            return mock_retrieve_response
        elif endpoint == 'ssl/generate/example.com':
            return mock_generate_response
        raise ValueError(f"Unexpected endpoint: {endpoint}")
    
    with patch('porkbun.commands.ssl.make_request', side_effect=side_effect) as mock_request:
        result = runner.invoke(ssl, ['generate', 'example.com'])
        assert result.exit_code == 0
        # Verify both calls were made in the right order
        assert mock_request.call_count == 2
        assert mock_request.call_args_list[0][0][0] == 'ssl/retrieve/example.com'
        assert mock_request.call_args_list[1][0][0] == 'ssl/generate/example.com'
        assert mock_request.call_args_list[1][0][1] == {}

def test_generate_validation_error(runner):
    """Test error handling when domain validation fails during generation"""
    # For the first retrieve call, return not found
    mock_retrieve_response = {"status": "ERROR", "message": "Certificate not found"}
    # For the generate call, return error
    mock_generate_response = {
        "status": "ERROR",
        "message": "Domain validation failed"
    }
    
    # Create a mock that returns different values based on the endpoint
    def side_effect(endpoint, data=None):
        if endpoint == 'ssl/retrieve/example.com':
            return mock_retrieve_response
        elif endpoint == 'ssl/generate/example.com':
            return mock_generate_response
        raise ValueError(f"Unexpected endpoint: {endpoint}")
    
    with patch('porkbun.commands.ssl.make_request', side_effect=side_effect) as mock_request:
        result = runner.invoke(ssl, ['generate', 'example.com'])
        assert result.exit_code == 0  # Command succeeds but shows error message
        assert mock_request.call_count == 2
        assert mock_request.call_args_list[0][0][0] == 'ssl/retrieve/example.com'
        assert mock_request.call_args_list[1][0][0] == 'ssl/generate/example.com'
        assert "Error generating certificate" in result.output

def test_generate_rate_limit(runner):
    """Test handling of rate limit errors during SSL certificate generation"""
    # For the first retrieve call, return not found
    mock_retrieve_response = {"status": "ERROR", "message": "Certificate not found"}
    
    # Create a mock that returns different values or raises exceptions based on the endpoint
    def side_effect(endpoint, data=None):
        if endpoint == 'ssl/retrieve/example.com':
            return mock_retrieve_response
        elif endpoint == 'ssl/generate/example.com':
            raise PorkbunAPIError("Rate limit exceeded")
        raise ValueError(f"Unexpected endpoint: {endpoint}")
    
    with patch('porkbun.commands.ssl.make_request', side_effect=side_effect) as mock_request:
        result = runner.invoke(ssl, ['generate', 'example.com'])
        assert result.exit_code == 0  # Command succeeds but shows error message
        assert mock_request.call_count == 2
        assert mock_request.call_args_list[0][0][0] == 'ssl/retrieve/example.com'
        assert "Error generating certificate" in result.output
        assert "Rate limit exceeded" in result.output

def test_retrieve_invalid_domain(runner):
    """Test error handling for invalid domain format"""
    result = runner.invoke(ssl, ['retrieve', 'invalid..domain'])
    assert result.exit_code == 2  # Click's error exit code
    assert "Invalid domain format" in result.output

def test_generate_invalid_domain(runner):
    """Test error handling for invalid domain format in generation"""
    result = runner.invoke(ssl, ['generate', 'invalid..domain'])
    assert result.exit_code == 2  # Click's error exit code
    assert "Invalid domain format" in result.output

def test_list_all_success(runner):
    """Test successful listing of SSL certificates"""
    mock_response = {
        "status": "SUCCESS",
        "certificates": [
            {
                "domain": "example.com",
                "certificate": {
                    "type": "Standard",
                    "notafter": "2024-12-31 00:00:00"
                }
            }
        ]
    }
    
    with patch('porkbun.commands.ssl.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(ssl, ['list-all'])
        assert result.exit_code == 0
        mock_request.assert_called_with('ssl/listAll', {})
        assert "example.com" in result.output

def test_expiring_success(runner):
    """Test successful listing of expiring certificates"""
    mock_response = {
        "status": "SUCCESS",
        "certificates": [
            {
                "domain": "example.com",
                "certificate": {
                    "type": "Standard",
                    "notafter": "2024-12-31 00:00:00"
                }
            }
        ]
    }
    
    with patch('porkbun.commands.ssl.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(ssl, ['expiring'])
        assert result.exit_code == 0
        mock_request.assert_called_with('ssl/listAll', {}) 
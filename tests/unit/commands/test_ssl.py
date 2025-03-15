"""Unit tests for SSL command functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

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
    mock_generate_response = {
        "status": "SUCCESS",
        "certificatechain": ["-----BEGIN CERTIFICATE-----\n..."],
        "privatekey": "-----BEGIN PRIVATE KEY-----\n..."
    }
    
    with patch('porkbun.commands.ssl.make_request') as mock_request:
        mock_request.return_value = mock_generate_response
        result = runner.invoke(ssl, ['generate', 'example.com'])
        assert result.exit_code == 0
        mock_request.assert_called_with('ssl/generate/example.com', {})

def test_generate_validation_error(runner):
    """Test error handling when domain validation fails during generation"""
    mock_response = {
        "status": "ERROR",
        "message": "Domain validation failed"
    }
    
    with patch('porkbun.commands.ssl.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(ssl, ['generate', 'example.com'])
        assert result.exit_code == 0  # Command succeeds but shows error message
        mock_request.assert_called_with('ssl/generate/example.com', {})
        assert "Error generating certificate" in result.output

def test_generate_rate_limit(runner):
    """Test handling of rate limit errors during SSL certificate generation"""
    with patch('porkbun.commands.ssl.make_request', side_effect=PorkbunAPIError("Rate limit exceeded")) as mock_request:
        result = runner.invoke(ssl, ['generate', 'example.com'])
        assert result.exit_code == 0  # Command succeeds but shows error message
        mock_request.assert_called_with('ssl/generate/example.com', {})
        assert "Error generating certificate" in result.output

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
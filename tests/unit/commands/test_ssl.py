"""Unit tests for SSL command functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from porkbun.commands.ssl import retrieve_bundle

@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()

def test_retrieve_bundle_success(runner):
    """Test successful retrieval of SSL certificate"""
    mock_response = {
        "status": "success",
        "certificatechain": "-----BEGIN CERTIFICATE-----\n...",
        "intermediatecertificate": "-----BEGIN CERTIFICATE-----\n...",
        "privatekey": "-----BEGIN PRIVATE KEY-----\n...",
        "publickey": "-----BEGIN PUBLIC KEY-----\n..."
    }
    
    with patch('porkbun.commands.ssl.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(retrieve_bundle, ['example.com'])
        assert result.exit_code == 0
        mock_request.assert_called_once_with('ssl/retrieve', {'domain': 'example.com'})
        assert str(mock_response) in result.output

def test_retrieve_bundle_error(runner):
    """Test error handling when SSL certificate is not found"""
    mock_response = {
        "status": "error",
        "message": "SSL certificate not found"
    }
    
    with patch('porkbun.commands.ssl.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(retrieve_bundle, ['example.com'])
        assert result.exit_code == 0  # CLI commands typically return 0 even for API errors
        mock_request.assert_called_once_with('ssl/retrieve', {'domain': 'example.com'})
        assert str(mock_response) in result.output 
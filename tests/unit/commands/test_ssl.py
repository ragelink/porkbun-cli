"""Unit tests for SSL command functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from porkbun.commands.ssl import retrieve_bundle, generate_bundle
from porkbun.utils.exceptions import PorkbunAPIError

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
        assert result.exit_code == 1  # Should fail with error status
        mock_request.assert_called_once_with('ssl/retrieve', {'domain': 'example.com'})
        assert str(mock_response) in result.output

def test_generate_bundle_success(runner):
    """Test successful generation of SSL certificate"""
    mock_generate_response = {
        "status": "success",
        "message": "Certificate generation initiated"
    }
    mock_retrieve_response = {
        "status": "success",
        "certificatechain": "-----BEGIN CERTIFICATE-----\n...",
        "intermediatecertificate": "-----BEGIN CERTIFICATE-----\n...",
        "privatekey": "-----BEGIN PRIVATE KEY-----\n...",
        "publickey": "-----BEGIN PUBLIC KEY-----\n..."
    }
    
    with patch('porkbun.commands.ssl.make_request') as mock_request:
        mock_request.side_effect = [mock_generate_response, mock_retrieve_response]
        result = runner.invoke(generate_bundle, ['example.com'])
        assert result.exit_code == 0
        assert len(mock_request.call_args_list) == 2
        
        # Check generate call
        generate_call = mock_request.call_args_list[0]
        assert generate_call[0][0] == 'ssl/generate'
        assert generate_call[0][1] == {'domain': 'example.com'}
        
        # Check retrieve call
        retrieve_call = mock_request.call_args_list[1]
        assert retrieve_call[0][0] == 'ssl/retrieve'
        assert retrieve_call[0][1] == {'domain': 'example.com'}

def test_generate_bundle_validation_error(runner):
    """Test error handling when domain validation fails during generation"""
    mock_response = {
        "status": "error",
        "message": "Domain validation failed"
    }
    
    with patch('porkbun.commands.ssl.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(generate_bundle, ['example.com'])
        assert result.exit_code == 1  # Should fail on validation error
        mock_request.assert_called_once_with('ssl/generate', {'domain': 'example.com'})
        assert "Domain validation failed" in result.output

def test_generate_bundle_rate_limit(runner):
    """Test handling of rate limit errors during SSL certificate generation"""
    with patch('porkbun.commands.ssl.make_request', side_effect=PorkbunAPIError("Rate limit exceeded")) as mock_request:
        result = runner.invoke(generate_bundle, ['example.com'])
        assert result.exit_code == 1
        mock_request.assert_called_once_with('ssl/generate', {'domain': 'example.com'})
        assert "Rate limit exceeded" in result.output

def test_retrieve_bundle_invalid_domain(runner):
    """Test error handling for invalid domain format"""
    result = runner.invoke(retrieve_bundle, ['invalid..domain'])
    assert result.exit_code == 2  # Click's error exit code
    assert "Invalid domain format" in result.output

def test_generate_bundle_invalid_domain(runner):
    """Test error handling for invalid domain format in generation"""
    result = runner.invoke(generate_bundle, ['invalid..domain'])
    assert result.exit_code == 2  # Click's error exit code
    assert "Invalid domain format" in result.output 
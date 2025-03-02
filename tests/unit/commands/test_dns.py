"""Unit tests for DNS command functionality."""

import pytest
import json
from click.testing import CliRunner
from unittest.mock import patch

from porkbun.commands.dns import retrieve, create_record, retrieve_records, update_record, delete_record
from porkbun.utils.exceptions import PorkbunAPIError

@pytest.fixture
def runner():
    return CliRunner()

def test_retrieve_success(runner):
    """Test successful retrieval of DNS records"""
    mock_response = {
        "status": "success",
        "records": [
            {"id": "123", "type": "A", "content": "1.2.3.4", "ttl": "600"},
            {"id": "124", "type": "MX", "content": "mail.example.com", "ttl": "3600"}
        ]
    }
    
    with patch('porkbun.commands.dns.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(retrieve, ['example.com'])
        assert result.exit_code == 0
        mock_request.assert_called_once_with('dns/retrieve/example.com', {})
        assert str(mock_response) in result.output

def test_create_record_success(runner):
    """Test successful creation of DNS record"""
    mock_response = {
        "status": "success",
        "id": "125"
    }
    
    with patch('porkbun.commands.dns.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(create_record, ['example.com', 'A', '1.2.3.4', '600'])
        assert result.exit_code == 0
        mock_request.assert_called_once_with('dns/create', {
            'domain': 'example.com',
            'type': 'A',
            'content': '1.2.3.4',
            'ttl': '600'
        })
        assert str(mock_response) in result.output

def test_retrieve_records_success(runner):
    """Test successful retrieval of all DNS records"""
    mock_response = {
        "status": "success",
        "records": [
            {"id": "123", "type": "A", "content": "1.2.3.4", "ttl": "600"},
            {"id": "124", "type": "MX", "content": "mail.example.com", "ttl": "3600"}
        ]
    }
    
    with patch('porkbun.commands.dns.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(retrieve_records, ['example.com'])
        assert result.exit_code == 0
        mock_request.assert_called_once_with('dns/retrieve', {'domain': 'example.com'})
        assert str(mock_response) in result.output

def test_update_record_success(runner):
    """Test successful update of DNS record"""
    mock_response = {
        "status": "success"
    }
    
    with patch('porkbun.commands.dns.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(update_record, [
            'example.com',
            '--record-id', '123',
            '--record-type', 'A',
            '--content', '5.6.7.8',
            '--ttl', '300'
        ])
        assert result.exit_code == 0
        mock_request.assert_called_once_with('dns/update', {
            'domain': 'example.com',
            'id': '123',
            'type': 'A',
            'content': '5.6.7.8',
            'ttl': '300'
        })
        assert str(mock_response) in result.output

def test_delete_record_success(runner):
    """Test successful deletion of DNS record"""
    mock_response = {
        "status": "success"
    }
    
    with patch('porkbun.commands.dns.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(delete_record, ['example.com', '123'])
        assert result.exit_code == 0
        mock_request.assert_called_once_with('dns/delete', {
            'domain': 'example.com',
            'id': '123'
        })
        assert str(mock_response) in result.output

def test_retrieve_error(runner):
    """Test error handling when retrieving DNS records"""
    mock_response = {
        "status": "error",
        "message": "Domain not found"
    }
    
    with patch('porkbun.commands.dns.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(retrieve, ['example.com'])
        assert result.exit_code == 0  # CLI commands typically return 0 even for API errors
        mock_request.assert_called_once_with('dns/retrieve/example.com', {})
        assert str(mock_response) in result.output

def test_update_record_not_found(runner):
    """Test error handling when updating non-existent DNS record"""
    mock_response = {
        "status": "error",
        "message": "Record not found"
    }
    
    with patch('porkbun.commands.dns.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(update_record, [
            'example.com',
            '--record-id', '999',
            '--record-type', 'A',
            '--content', '1.2.3.4',
            '--ttl', '600'
        ])
        assert result.exit_code == 0  # CLI commands typically return 0 even for API errors
        mock_request.assert_called_once_with('dns/update', {
            'domain': 'example.com',
            'id': '999',
            'type': 'A',
            'content': '1.2.3.4',
            'ttl': '600'
        })
        assert str(mock_response) in result.output

def test_create_record_invalid_type(runner):
    """Test error handling for invalid DNS record type"""
    result = runner.invoke(create_record, ['example.com', 'INVALID', '1.2.3.4', '600'])
    assert result.exit_code == 2  # Click's error exit code
    assert "Invalid record type" in result.output

def test_create_record_invalid_ttl(runner):
    """Test error handling for invalid TTL value"""
    result = runner.invoke(create_record, ['example.com', 'A', '1.2.3.4', '0'])
    assert result.exit_code == 2
    assert "TTL must be a positive integer" in result.output

def test_create_record_invalid_ip(runner):
    """Test error handling for invalid IP address in A record"""
    result = runner.invoke(create_record, ['example.com', 'A', 'invalid.ip', '600'])
    assert result.exit_code == 2
    assert "Invalid IP address format" in result.output

def test_create_record_rate_limit(runner):
    """Test handling of rate limit errors"""
    with patch('porkbun.commands.dns.make_request', side_effect=PorkbunAPIError("Rate limit exceeded")) as mock_request:
        result = runner.invoke(create_record, ['example.com', 'A', '1.2.3.4', '600'])
        assert result.exit_code == 1
        mock_request.assert_called_once()
        assert "Rate limit exceeded" in result.output

def test_bulk_update_records(runner):
    """Test bulk update of DNS records"""
    mock_response = {
        "status": "success"
    }
    
    records = [
        {"id": "123", "type": "A", "content": "1.2.3.4", "ttl": "600"},
        {"id": "124", "type": "MX", "content": "mail.example.com", "ttl": "3600"}
    ]
    
    with patch('porkbun.commands.dns.make_request', return_value=mock_response) as mock_request:
        result = runner.invoke(update_record, [
            'example.com',
            '--records', json.dumps(records)
        ])
        print(f"Result output: {result.output}")
        print(f"Result exception: {result.exception}")
        assert result.exit_code == 0
        assert mock_request.call_count == 2  # One call per record
        assert "Updated record 123" in result.output
        assert "Updated record 124" in result.output
        
        # Verify the API calls
        calls = mock_request.call_args_list
        assert calls[0][0][0] == 'dns/update'
        assert calls[0][0][1] == {
            'domain': 'example.com',
            'id': '123',
            'type': 'A',
            'content': '1.2.3.4',
            'ttl': '600'
        }
        assert calls[1][0][0] == 'dns/update'
        assert calls[1][0][1] == {
            'domain': 'example.com',
            'id': '124',
            'type': 'MX',
            'content': 'mail.example.com',
            'ttl': '3600'
        }

def test_invalid_domain_format(runner):
    """Test error handling for invalid domain format"""
    result = runner.invoke(retrieve, ['invalid..domain'])
    assert result.exit_code == 2
    assert "Invalid domain format" in result.output 
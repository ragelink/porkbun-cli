"""Unit tests for DNS command functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch

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
        result = runner.invoke(update_record, ['example.com', '123', 'A', '5.6.7.8', '300'])
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

@pytest.mark.unit
class TestDNSCommands:
    """Test DNS management commands."""
    
    def test_list_records_success(self, cli_runner, mock_session, sample_domain, mock_dns_records):
        """Test successful DNS record listing."""
        mock_session.post.return_value.json.return_value = {
            "status": "SUCCESS",
            "records": mock_dns_records
        }
        
        with patch('porkbun.commands.dns.make_request') as mock_request:
            mock_request.return_value = mock_session.post.return_value.json.return_value
            result = cli_runner.invoke(retrieve, [sample_domain])
            
            assert result.exit_code == 0
            assert "www" in result.output
            assert "192.0.2.1" in result.output
            assert "mail" in result.output
            mock_request.assert_called_once_with(f"dns/retrieve/{sample_domain}", {})
    
    def test_list_records_error(self, cli_runner, mock_session, sample_domain):
        """Test DNS record listing with API error."""
        mock_session.post.return_value.json.return_value = {
            "status": "ERROR",
            "message": "API Error"
        }
        
        with patch('porkbun.commands.dns.make_request') as mock_request:
            mock_request.return_value = mock_session.post.return_value.json.return_value
            result = cli_runner.invoke(retrieve, [sample_domain])
            
            assert result.exit_code != 0
            assert "API Error" in result.output
    
    def test_create_record_success(self, cli_runner, mock_session, sample_domain):
        """Test successful DNS record creation."""
        mock_session.post.return_value.json.return_value = {
            "status": "SUCCESS"
        }
        
        with patch('porkbun.commands.dns.make_request') as mock_request:
            mock_request.return_value = mock_session.post.return_value.json.return_value
            result = cli_runner.invoke(create_record, [
                sample_domain,
                '--type', 'A',
                '--name', 'test',
                '--content', '192.0.2.1',
                '--ttl', '600'
            ])
            
            assert result.exit_code == 0
            assert "Successfully created" in result.output
            mock_request.assert_called_once_with(
                f"dns/create/{sample_domain}",
                {
                    "type": "A",
                    "name": "test",
                    "content": "192.0.2.1",
                    "ttl": 600
                }
            )
    
    def test_delete_record_success(self, cli_runner, mock_session, sample_domain):
        """Test successful DNS record deletion."""
        record_id = "123"
        mock_session.post.return_value.json.return_value = {
            "status": "SUCCESS"
        }
        
        with patch('porkbun.commands.dns.make_request') as mock_request:
            mock_request.return_value = mock_session.post.return_value.json.return_value
            result = cli_runner.invoke(delete_record, [sample_domain, record_id])
            
            assert result.exit_code == 0
            assert "Successfully deleted" in result.output
            mock_request.assert_called_once_with(f"dns/delete/{sample_domain}/{record_id}", {})
    
    def test_edit_record_success(self, cli_runner, mock_session, sample_domain, mock_dns_records):
        """Test successful DNS record editing."""
        record_id = "123"
        mock_session.post.return_value.json.return_value = {
            "status": "SUCCESS",
            "records": mock_dns_records
        }
        
        with patch('porkbun.commands.dns.make_request') as mock_request:
            # First call returns current records
            mock_request.side_effect = [
                {"status": "SUCCESS", "records": mock_dns_records},
                {"status": "SUCCESS"}
            ]
            
            result = cli_runner.invoke(update_record, [
                sample_domain,
                record_id,
                '--content', '192.0.2.2'
            ])
            
            assert result.exit_code == 0
            assert "Successfully updated" in result.output
            assert len(mock_request.call_args_list) == 2  # Two API calls made
            
            # Verify the edit request
            edit_call = mock_request.call_args_list[1]
            assert edit_call[0][0] == f"dns/edit/{sample_domain}/{record_id}"
            assert edit_call[0][1]["content"] == "192.0.2.2"
            assert edit_call[0][1]["type"] == "A"  # Preserved from existing record
    
    def test_edit_record_not_found(self, cli_runner, mock_session, sample_domain):
        """Test editing non-existent DNS record."""
        record_id = "999"
        mock_session.post.return_value.json.return_value = {
            "status": "SUCCESS",
            "records": []
        }
        
        with patch('porkbun.commands.dns.make_request') as mock_request:
            mock_request.return_value = mock_session.post.return_value.json.return_value
            result = cli_runner.invoke(update_record, [
                sample_domain,
                record_id,
                '--content', '192.0.2.2'
            ])
            
            assert result.exit_code != 0
            assert "not found" in result.output 
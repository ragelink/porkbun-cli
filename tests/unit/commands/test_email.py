"""Unit tests for Email command functionality."""

import pytest
import json
from click.testing import CliRunner
from unittest.mock import patch, Mock

from porkbun.commands.email import (
    email,
    list_forwards,
    create_forward,
    update_forward,
    delete_forward,
    batch_create,
    batch_delete,
)
from porkbun.utils.exceptions import PorkbunAPIError

@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()

@pytest.fixture
def mock_email_forwards():
    """Sample email forwards response."""
    return {
        "status": "SUCCESS",
        "forwards": [
            {
                "id": "12345",
                "email": "info@example.com",
                "forward_to": "contact@example.com",
                "status": "active"
            },
            {
                "id": "67890",
                "email": "sales@example.com",
                "forward_to": "sales@example.com",
                "status": "active"
            },
        ]
    }

@pytest.fixture
def mock_empty_forwards():
    """Empty email forwards response."""
    return {
        "status": "SUCCESS",
        "forwards": []
    }

@pytest.fixture
def mock_success_response():
    """Mock success response."""
    return {
        "status": "SUCCESS"
    }

@pytest.fixture
def mock_error_response():
    """Mock error response."""
    return {
        "status": "ERROR",
        "message": "Sample error message"
    }

@pytest.fixture
def sample_domain():
    """Sample domain name."""
    return "example.com"

@pytest.mark.unit
class TestEmailCommands:
    """Test email forwarding commands."""
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_list_forwards(self, mock_run, runner, mock_email_forwards, sample_domain):
        """Test listing email forwards."""
        mock_run.return_value = mock_email_forwards
        
        result = runner.invoke(list_forwards, [sample_domain])
        
        assert result.exit_code == 0
        assert "Email Forwards for" in result.output
        assert "info@example.com" in result.output
        assert "sales@example.com" in result.output
        
        mock_run.assert_called_once_with(Mock())
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_list_forwards_empty(self, mock_run, runner, mock_empty_forwards, sample_domain):
        """Test listing empty email forwards."""
        mock_run.return_value = mock_empty_forwards
        
        result = runner.invoke(list_forwards, [sample_domain])
        
        assert result.exit_code == 0
        assert "No email forwards found" in result.output
        
        mock_run.assert_called_once_with(Mock())
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_create_forward(self, mock_run, runner, mock_success_response, sample_domain):
        """Test creating email forward."""
        mock_run.return_value = mock_success_response
        
        result = runner.invoke(create_forward, [sample_domain, "info", "contact@example.com"])
        
        assert result.exit_code == 0
        assert "Successfully created email forward" in result.output
        assert "info@example.com" in result.output
        assert "contact@example.com" in result.output
        
        mock_run.assert_called_once_with(Mock())
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_create_forward_with_invalid_email(self, mock_run, runner, sample_domain):
        """Test creating email forward with invalid email."""
        result = runner.invoke(create_forward, [sample_domain, "info", "invalid-email"])
        
        assert result.exit_code == 2
        assert "Invalid forwarding email address" in result.output
        
        mock_run.assert_not_called()
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_delete_forward(self, mock_run, runner, mock_success_response, sample_domain):
        """Test deleting email forward."""
        mock_run.return_value = mock_success_response
        
        result = runner.invoke(delete_forward, [sample_domain, "12345"])
        
        assert result.exit_code == 0
        assert "Successfully deleted email forward" in result.output
        assert "12345" in result.output
        
        mock_run.assert_called_once_with(Mock())
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_update_forward_success(self, mock_run, runner, mock_email_forwards, mock_success_response, sample_domain):
        """Test updating email forward."""
        # First call returns the list of forwards, second call is the update
        mock_run.side_effect = [mock_email_forwards, mock_success_response]
        
        result = runner.invoke(update_forward, [sample_domain, "12345", "new@example.com"])
        
        assert result.exit_code == 0
        assert "Successfully updated email forward" in result.output
        assert "info@example.com" in result.output
        assert "new@example.com" in result.output
        
        assert mock_run.call_count == 2
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_update_forward_not_found(self, mock_run, runner, mock_email_forwards, sample_domain):
        """Test updating non-existent email forward."""
        mock_run.return_value = mock_email_forwards
        
        result = runner.invoke(update_forward, [sample_domain, "99999", "new@example.com"])
        
        assert result.exit_code == 1
        assert "not found" in result.output
        
        mock_run.assert_called_once_with(Mock())
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_batch_create(self, mock_run, runner, mock_success_response, sample_domain, tmp_path):
        """Test batch creating email forwards."""
        mock_run.return_value = mock_success_response
        
        # Create test batch file
        batch_file = tmp_path / "email_forwards.json"
        batch_data = [
            {"email_prefix": "info", "forward_to": "contact@example.com"},
            {"email_prefix": "sales", "forward_to": "sales@example.com"}
        ]
        with open(batch_file, 'w') as f:
            json.dump(batch_data, f)
        
        result = runner.invoke(batch_create, [sample_domain, str(batch_file)])
        
        assert result.exit_code == 0
        assert "Successfully created all" in result.output
        assert "2 email forwards" in result.output
        
        assert mock_run.call_count == 2
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_batch_create_invalid_json(self, mock_run, runner, sample_domain, tmp_path):
        """Test batch creating with invalid JSON."""
        # Create test batch file with invalid JSON
        batch_file = tmp_path / "invalid.json"
        with open(batch_file, 'w') as f:
            f.write("{invalid json")
        
        result = runner.invoke(batch_create, [sample_domain, str(batch_file)])
        
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output
        
        mock_run.assert_not_called()
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_batch_delete(self, mock_run, runner, mock_success_response, sample_domain):
        """Test batch deleting email forwards."""
        mock_run.return_value = mock_success_response
        
        result = runner.invoke(batch_delete, [sample_domain, "12345", "67890"])
        
        assert result.exit_code == 0
        assert "Successfully deleted all" in result.output
        assert "2 email forwards" in result.output
        
        assert mock_run.call_count == 2
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_batch_delete_no_ids(self, mock_run, runner, sample_domain):
        """Test batch deleting with no IDs provided."""
        result = runner.invoke(batch_delete, [sample_domain])
        
        assert result.exit_code == 1
        assert "No email IDs provided" in result.output
        
        mock_run.assert_not_called()
    
    @patch('porkbun.commands.email.asyncio.run')
    def test_error_handling(self, mock_run, runner, sample_domain):
        """Test API error handling."""
        mock_run.side_effect = PorkbunAPIError("API error occurred")
        
        result = runner.invoke(list_forwards, [sample_domain])
        
        assert result.exit_code == 1
        assert "Error: API error occurred" in result.output 
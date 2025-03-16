"""
Unit tests for the setup_domain_services.py script
"""

import json
import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from examples.setup_domain_services import setup_domain_with_service


@pytest.fixture
def setup_test_environment():
    """Create test environment with templates directory and sample files"""
    test_dir = tempfile.mkdtemp()
    templates_dir = os.path.join(test_dir, "templates")
    os.makedirs(templates_dir)
    
    # Create sample templates
    services = ["cloudflare", "google", "microsoft"]
    
    for service in services:
        template = [
            {
                "type": "A",
                "name": "@",
                "content": "192.0.2.1",
                "ttl": 3600
            },
            {
                "type": "MX",
                "name": "@",
                "content": "DOMAIN-com.mail.protection.outlook.com" if service == "microsoft" else "mail.example.com",
                "ttl": 3600,
                "priority": 10
            }
        ]
        
        template_path = os.path.join(templates_dir, f"{service}_dns.json")
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
    
    yield test_dir
    
    # Clean up
    shutil.rmtree(test_dir)


@patch("examples.setup_domain_services.Path")
@patch("examples.setup_domain_services.customize_template")
@patch("examples.setup_domain_services.subprocess.run")
def test_setup_domain_with_service(mock_subprocess_run, mock_customize, mock_path, setup_test_environment):
    """Test setting up a domain with a specific service"""
    # Configure mocks
    mock_subprocess_run.return_value = MagicMock(returncode=0)
    mock_customize.return_value = "customized_template.json"
    
    # Set up Path mock to return our test directory
    mock_path.side_effect = lambda x: Path(x) if isinstance(x, str) else x
    mock_path.return_value.parent.return_value = Path(setup_test_environment)
    
    # Run the function with dry run
    result = setup_domain_with_service(
        "example.com", 
        "microsoft", 
        output_dir=os.path.join(setup_test_environment, "output"),
        dry_run=True
    )
    
    # Verify results
    assert result is True
    mock_customize.assert_called_once()
    mock_subprocess_run.assert_not_called()  # Should not be called in dry run mode


@patch("examples.setup_domain_services.Path")
@patch("examples.setup_domain_services.customize_template")
@patch("examples.setup_domain_services.subprocess.run")
def test_setup_domain_with_service_apply(mock_subprocess_run, mock_customize, mock_path, setup_test_environment):
    """Test setting up a domain with a specific service and actually applying it"""
    # Configure mocks
    mock_subprocess_run.return_value = MagicMock(returncode=0)
    mock_customize.return_value = "customized_template.json"
    
    # Set up Path mock to return our test directory
    mock_path.side_effect = lambda x: Path(x) if isinstance(x, str) else x
    mock_path.return_value.parent.return_value = Path(setup_test_environment)
    
    # Run the function with actual apply
    result = setup_domain_with_service(
        "example.com", 
        "microsoft", 
        output_dir=os.path.join(setup_test_environment, "output"),
        dry_run=False
    )
    
    # Verify results
    assert result is True
    mock_customize.assert_called_once()
    mock_subprocess_run.assert_called_once()
    
    # Check command arguments
    args, kwargs = mock_subprocess_run.call_args
    cmd = args[0]
    assert "workflow" in cmd
    assert "setup-domain" in cmd
    assert "example.com" in cmd
    assert "--dns-records" in cmd
    assert kwargs.get("check") is True


@patch("examples.setup_domain_services.Path")
@patch("examples.setup_domain_services.customize_template")
@patch("examples.setup_domain_services.subprocess.run")
def test_setup_domain_with_invalid_service(mock_subprocess_run, mock_customize, mock_path, setup_test_environment):
    """Test handling of invalid service name"""
    # Set up Path mock to return our test directory
    mock_path.side_effect = lambda x: Path(x) if isinstance(x, str) else x
    mock_path.return_value.parent.return_value = Path(setup_test_environment)
    
    # Run with invalid service
    result = setup_domain_with_service(
        "example.com", 
        "nonexistent_service", 
        output_dir=os.path.join(setup_test_environment, "output"),
        dry_run=True
    )
    
    # Verify results
    assert result is False
    mock_customize.assert_not_called()
    mock_subprocess_run.assert_not_called()


@patch("examples.setup_domain_services.subprocess.run")
def test_setup_domain_command_error(mock_subprocess_run, setup_test_environment):
    """Test handling of command execution error"""
    # Configure mock to simulate a command failure
    mock_subprocess_run.side_effect = Exception("Command failed")
    
    with patch("examples.setup_domain_services.Path") as mock_path:
        # Set up Path mock to return our test directory
        mock_path.side_effect = lambda x: Path(x) if isinstance(x, str) else x
        mock_path.return_value.parent.return_value = Path(setup_test_environment)
        
        with patch("examples.setup_domain_services.customize_template") as mock_customize:
            mock_customize.return_value = "customized_template.json"
            
            # Run the function
            result = setup_domain_with_service(
                "example.com", 
                "microsoft", 
                output_dir=os.path.join(setup_test_environment, "output"),
                dry_run=False
            )
            
            # Verify results
            assert result is False
            mock_customize.assert_called_once()
            mock_subprocess_run.assert_called_once() 
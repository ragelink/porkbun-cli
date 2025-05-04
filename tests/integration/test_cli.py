import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock, MagicMock
import json
import os
from pathlib import Path
import signal

from porkbun.cli import cli
from porkbun.utils.config import ConfigManager
from porkbun.utils.security import security_manager

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_config():
    # We need to patch both places where ConfigManager is used
    with patch('porkbun.cli.ConfigManager') as cli_mock:
        # Mock the CLI module's ConfigManager
        cli_instance = cli_mock.return_value
        cli_instance.get_profile.return_value.api_key = 'test_api_key'
        cli_instance.get_profile.return_value.secret_key = 'test_secret_key'
        cli_instance.load = MagicMock()
        cli_instance.set_current_profile = MagicMock()
        
        # Now patch the config command's ConfigManager
        with patch('porkbun.commands.config.ConfigManager') as config_mock:
            # Create a separate instance for the config command
            config_instance = config_mock.return_value
            config_instance.profile_exists = MagicMock(return_value=False)
            config_instance.add_profile = MagicMock(return_value=True)
            config_instance.set_current_profile = MagicMock()
            config_instance.load = MagicMock()
            
            # Return both mocks for testing
            yield {
                "cli": cli_mock,
                "config": config_mock
            }

@pytest.fixture
def temp_config(tmp_path):
    config_dir = tmp_path / '.porkbun'
    config_dir.mkdir()
    old_home = os.environ.get('HOME')
    os.environ['HOME'] = str(tmp_path)
    yield tmp_path
    if old_home:
        os.environ['HOME'] = old_home

def test_cli_version(runner):
    """Test CLI version command."""
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert 'version' in result.output.lower()

def test_config_add_profile(runner, temp_config):
    """Test adding a new profile."""
    # We need to patch the add_profile method implementation
    with patch('porkbun.commands.config.config_manager.add_profile') as mock_add:
        # Run the command
        result = runner.invoke(cli, [
            'config', 'add', 'test',
            '--api-key', 'test_key',
            '--secret-key', 'test_secret'
        ])
        
        # Check results
        assert result.exit_code == 0
        mock_add.assert_called_once_with(
            name='test',
            api_key='test_key',
            secret_key='test_secret',
            base_url=None,
            make_default=False
        )

def test_domains_check(runner, mock_config):
    """Test domain check command."""
    mock_response = {
        'status': 'SUCCESS',
        'response': {'avail': 'yes', 'price': 10.00}
    }
    
    with patch('porkbun.commands.domains.make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        # Use patch context manager for get_tld_pricing to avoid nested async issues
        with patch('porkbun.commands.domains.get_tld_pricing', return_value={}):
            result = runner.invoke(cli, ['domains', 'check', 'example.com', '--no-suggest', '--no-compare'])
            assert result.exit_code == 0
            assert 'example.com' in result.output

def test_dns_list(runner, mock_config):
    """Test DNS record listing."""
    mock_response = {
        'status': 'SUCCESS',
        'records': [
            {
                'name': '@',
                'type': 'A',
                'content': '1.2.3.4',
                'ttl': '600'
            }
        ]
    }
    
    with patch('porkbun.commands.dns.make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        result = runner.invoke(cli, ['dns', 'retrieve', 'example.com'])
        assert result.exit_code == 0
        assert 'A' in result.output
        assert '1.2.3.4' in result.output

def test_ssl_list(runner, mock_config):
    """Test SSL certificate listing."""
    mock_response = {
        'status': 'SUCCESS',
        'certificates': [
            {
                'domain': 'example.com',
                'expires': '2024-12-31',
                'type': 'standard'
            }
        ]
    }
    
    with patch('porkbun.commands.ssl.make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        result = runner.invoke(cli, ['ssl', 'retrieve', 'example.com'])
        assert result.exit_code == 0
        assert 'example.com' in result.output or 'certificate' in result.output.lower()

@pytest.mark.timeout(5)  # Timeout after 5 seconds
def test_monitor_health(runner, mock_config):
    """Test health monitoring command."""
    # Use a simple mock for the requests.get call
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.elapsed = MockElapsed()
        
        def raise_for_status(self):
            pass
    
    class MockElapsed:
        def total_seconds(self):
            return 0.1
    
    # We'll patch requests.get to return our mock response
    with patch('requests.get', return_value=MockResponse()) as mock_request:
        # Run with test-mode flag so it exits after one check
        result = runner.invoke(cli, [
            'monitor', 'health', 'example.com',
            '--test-mode',
            '--timeout', '1'
        ])
        
        assert result.exit_code == 0
        assert 'Status' in result.output
        assert 'Health check completed' in result.output
        mock_request.assert_called_with('https://example.com/', timeout=1)

def test_automation_script(runner, mock_config, temp_config):
    """Test automation script execution."""
    script_file = temp_config / 'test_script.yaml'
    script_content = """
    steps:
      - name: Test step
        command: echo "test"
    """
    script_file.write_text(script_content)
    
    result = runner.invoke(cli, [
        'automation', 'script',
        str(script_file),
        '--dry-run'
    ])
    assert result.exit_code == 0
    assert 'Would execute: echo "test"' in result.output

def test_error_handling(runner):
    """Test error handling for invalid commands."""
    result = runner.invoke(cli, ['invalid'])
    assert result.exit_code == 2
    assert 'Error' in result.output

def test_debug_mode(runner, mock_config):
    """Test debug mode logging."""
    cli_mock = mock_config["cli"]
    
    with patch('porkbun.utils.logging.setup_logging') as mock_logging:
        # First make sure setup_logging is actually called
        with patch('porkbun.cli.setup_logging') as mock_setup:
            result = runner.invoke(cli, ['--debug', 'config', 'list'])
            mock_setup.assert_called_with(debug=True, log_file=None)
            assert result.exit_code == 0

def test_profile_switching(runner):
    """Test profile switching."""
    # Directly patch the set_current_profile method of the config_manager instance in cli.py
    with patch('porkbun.cli.config_manager.set_current_profile') as mock_set_profile:
        # Run with --profile option
        result = runner.invoke(cli, [
            '--profile', 'test',
            'config', 'show'
        ])
        
        # Check results
        assert result.exit_code == 0
        mock_set_profile.assert_called_once_with('test') 
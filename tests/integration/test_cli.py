import pytest
from click.testing import CliRunner
from unittest.mock import patch
import json
import os
from pathlib import Path

from porkbun.cli import cli
from porkbun.utils.config import ConfigManager
from porkbun.utils.security import security_manager

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_config():
    with patch('porkbun.utils.config.ConfigManager') as mock:
        mock.return_value.get_profile.return_value.api_key = 'test_api_key'
        mock.return_value.get_profile.return_value.secret_key = 'test_secret_key'
        yield mock

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

def test_config_add_profile(runner, temp_config, mock_config):
    """Test adding a new profile."""
    result = runner.invoke(cli, [
        'config', 'add', 'test',
        '--api-key', 'test_key',
        '--secret-key', 'test_secret'
    ])
    assert result.exit_code == 0
    assert 'Added profile: test' in result.output
    mock_config.return_value.add_profile.assert_called_once_with(
        name='test',
        api_key='test_key',
        secret_key='test_secret',
        base_url=None,
        make_default=False
    )

def test_domains_check(runner, mock_config):
    """Test domain check command."""
    with patch('porkbun.commands.domains.make_request') as mock_request:
        mock_request.return_value = {
            'status': 'SUCCESS',
            'available': True,
            'price': 10.00
        }
        result = runner.invoke(cli, ['domains', 'check', 'example.com'])
        assert result.exit_code == 0
        assert 'example.com' in result.output

def test_dns_list(runner, mock_config):
    """Test DNS record listing."""
    with patch('porkbun.commands.dns.make_request') as mock_request:
        mock_request.return_value = {
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
        result = runner.invoke(cli, ['dns', 'list', 'example.com'])
        assert result.exit_code == 0
        assert 'A' in result.output
        assert '1.2.3.4' in result.output

def test_ssl_list(runner, mock_config):
    """Test SSL certificate listing."""
    with patch('porkbun.commands.ssl.make_request') as mock_request:
        mock_request.return_value = {
            'status': 'SUCCESS',
            'certificates': [
                {
                    'domain': 'example.com',
                    'expires': '2024-12-31',
                    'type': 'standard'
                }
            ]
        }
        result = runner.invoke(cli, ['ssl', 'list'])
        assert result.exit_code == 0
        assert 'example.com' in result.output

def test_monitor_health(runner, mock_config):
    """Test health monitoring command."""
    with patch('requests.get') as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.elapsed.total_seconds.return_value = 0.1
        
        result = runner.invoke(cli, [
            'monitor', 'health', 'example.com',
            '--timeout', '1'
        ], input='\x03')  # Send Ctrl+C to stop monitoring
        assert result.exit_code == 0
        assert 'Status' in result.output

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
    with patch('porkbun.utils.logging.setup_logging') as mock_logging:
        result = runner.invoke(cli, ['--debug', 'config', 'list'])
        mock_logging.assert_called_with(debug=True, log_file=None)
        assert result.exit_code == 0

def test_profile_switching(runner, mock_config):
    """Test profile switching."""
    result = runner.invoke(cli, [
        '--profile', 'test',
        'config', 'show'
    ])
    assert result.exit_code == 0
    mock_config.return_value.set_current_profile.assert_called_with('test') 
"""Integration tests for Email command functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from porkbun.commands.email import email, retrieve, create_forward

@pytest.fixture
def runner():
    return CliRunner()

def test_email_command_group():
    """Test that email command group has expected subcommands."""
    assert hasattr(email, 'commands')
    command_names = [cmd.name for cmd in email.commands]
    assert 'retrieve' in command_names
    assert 'create-forward' in command_names 
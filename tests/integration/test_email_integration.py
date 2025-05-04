"""Integration tests for Email command functionality."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from porkbun.commands.email import email

@pytest.fixture
def runner():
    return CliRunner()

def test_email_command_group():
    """Test that email command group has expected subcommands."""
    assert hasattr(email, 'commands')
    # Get command names from the Click group
    command_names = list(email.commands.keys())
    assert 'list-forwards' in command_names
    assert 'create-forward' in command_names 
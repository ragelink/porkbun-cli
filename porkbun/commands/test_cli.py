import unittest
from click.testing import CliRunner
from porkbun.cli import cli

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_list_all_domains(self):
        result = self.runner.invoke(cli, ['domains', 'list_all'])
        self.assertEqual(result.exit_code, 0)

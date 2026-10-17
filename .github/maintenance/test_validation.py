import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('validation', Path(__file__).with_name('validation.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ValidationTests(unittest.TestCase):
    def test_yaml_12_and_scalar_types(self):
        self.assertEqual(m.workflow_data('on: [push]'), m.workflow_data('"on": ["push"]'))
        self.assertNotEqual(m.workflow_data('key: true'), m.workflow_data('key: 1'))
        self.assertNotEqual(m.workflow_data('key: "on"'), m.workflow_data('key: true'))
        with self.assertRaises(RuntimeError):
            m.workflow_data('on: push\non: pull_request')

    def test_yaml_12_integer_resolution(self):
        self.assertNotEqual(m.workflow_data('key: 012'), m.workflow_data('key: 10'))
        self.assertEqual(m.workflow_data('key: 012'), m.workflow_data('key: 12'))
        self.assertEqual(m.workflow_data('key: 0o14'), m.workflow_data('key: 12'))
        self.assertEqual(m.workflow_data('key: 0xC'), m.workflow_data('key: 12'))
        self.assertEqual(m.workflow_data('key: +012'), m.workflow_data('key: 12'))

    def test_yaml_12_legacy_scalars_are_strings(self):
        for value in ['1:20', '2001-12-15', '2001-12-15T02:59:43.1Z', '0b11', '1_000']:
            with self.subTest(value=value):
                self.assertEqual(m.workflow_data(f'key: {value}'), m.workflow_data(f'key: "{value}"'))
        self.assertNotEqual(m.workflow_data('key: 1:20'), m.workflow_data('key: 80'))

    def test_yaml_float_types_and_precision_preserved(self):
        self.assertNotEqual(m.workflow_data('key: 1e3'), m.workflow_data('key: "1e3"'))
        self.assertNotEqual(m.workflow_data('key: 9007199254740992.0'),
                            m.workflow_data('key: 9007199254740993.0'))
        with self.assertRaises(RuntimeError):
            m.workflow_data('key: !!int 1:20')

    def test_package_commands_do_not_receive_secrets(self):
        secrets = {'GH_TOKEN': 'dummy-gh', 'GITHUB_TOKEN': 'dummy-github', 'OPENAI_API_KEY': 'dummy-provider'}
        with patch.dict(os.environ, secrets), patch.object(m.subprocess, 'run') as command:
            command.return_value.stdout = ''
            for binary in ['npm', 'node_modules/.bin/prettier']:
                m.run(binary, '--version')
                self.assertFalse(set(secrets) & set(command.call_args.kwargs['env']))

    def test_yaml_run_script_and_expression_preserved(self):
        before = 'on: push\njobs:\n  test:\n    if: ${{ github.ref == \'main\' }}\n    steps:\n      - run: |\n          echo one\n          echo two\n'
        after = before.replace('on: push', '"on": "push"')
        self.assertEqual(m.workflow_data(before), m.workflow_data(after))
        self.assertNotEqual(m.workflow_data(before), m.workflow_data(before.replace('echo two', 'echo three')))


if __name__ == '__main__':
    unittest.main()

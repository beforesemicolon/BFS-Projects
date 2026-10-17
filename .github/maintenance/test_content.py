import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('content', Path(__file__).with_name('content.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class ContentTests(unittest.TestCase):
    def test_extensionless_snippets_selected_with_spaces(self):
        files = ['README.md', 'LICENSE', '.gitignore', 'deep clone', 'some-snippet', '.github/script.py']
        self.assertEqual(c.source_files(files, 'javascript-solutions'), ['deep clone', 'some-snippet'])

    def test_nested_javascript_selected(self):
        files = ['tree.js', 'demo/app.js', 'demo/app.ts', '.github/script.js']
        self.assertEqual(c.source_files(files, 'tutorials-files'), ['tree.js', 'demo/app.js'])
        self.assertEqual(c.source_files(files, 'BFS-Projects'), [])

    def test_issue_scope_is_explicit_and_open(self):
        for text in ['Improve code', 'docs/README.md', 'README.md.bak']:
            self.assertFalse(c.supported_issue({'state': 'OPEN', 'title': text}))
        self.assertTrue(c.supported_issue({'state': 'OPEN', 'title': 'Clarify `README.md`'}))
        self.assertFalse(c.supported_issue({'state': 'CLOSED', 'title': 'README.md'}))

    def test_syntax_check_does_not_execute_snippet_and_strips_secrets(self):
        with patch.object(c.guard, 'content', return_value='throw new Error("never execute");'), patch.dict(os.environ, {'GH_TOKEN': 'x', 'OPENAI_API_KEY': 'y'}), patch.object(c.subprocess, 'run') as run:
            run.return_value.returncode = 0
            c.check_javascript('with spaces')
            self.assertEqual(run.call_args.args[0], ['node', '--check', '--input-type=module'])
            self.assertNotIn('GH_TOKEN', run.call_args.kwargs['env'])
            self.assertNotIn('OPENAI_API_KEY', run.call_args.kwargs['env'])

    def test_invalid_syntax_fails(self):
        with patch.object(c.guard, 'content', return_value='const x = {'), self.assertRaises(RuntimeError):
            c.check_javascript('broken snippet')

    def test_markdown_local_links_and_title(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = Path.cwd()
            try:
                os.chdir(directory)
                Path('target.txt').write_text('x')
                Path('README.md').write_text('# Test\n[local](target.txt) [web](https://example.com)')
                c.check_markdown('README.md')
                for text in ['', '# Title\n[missing](no.txt)', '# Title\n[bad](javascript:alert)', '# Title\n[escape](../outside)']:
                    Path('README.md').write_text(text)
                    with self.assertRaises(RuntimeError):
                        c.check_markdown('README.md')
            finally:
                os.chdir(previous)

    def test_documentation_agent_does_not_create_a_repository_map_cache(self):
        script = Path(__file__).with_name('content.sh').read_text()
        agent_command = next(line for line in script.splitlines() if ' agent aider ' in line)
        self.assertIn('--map-tokens 0', agent_command)
        self.assertIn('--no-suggest-shell-commands', agent_command)

    def test_default_branch_pushes_cannot_invoke_ai(self):
        workflow = Path(__file__).parents[1] / 'workflows/daily-ai-maintenance.yml'
        data = c.guard.yaml.load(workflow.read_text(), Loader=c.guard.WorkflowLoader)
        branches = {'BFS-Projects': 'development', 'javascript-solutions': 'main', 'tutorials-files': 'master'}
        self.assertEqual(data['on']['push']['branches'], [branches[c.profile()]])
        condition = data['jobs']['documentation']['if']
        self.assertIn("(github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')", condition)
        self.assertIn('github.ref_name == github.event.repository.default_branch', condition)

    def test_workflows_have_no_live_ai_on_pull_request_or_auto_merge(self):
        root = Path(__file__).parents[1]
        if not (root / 'workflows').exists():
            self.skipTest('Template has no installed workflows')
        for path in (root / 'workflows').glob('*.yml'):
            text = path.read_text()
            self.assertNotIn('continue-on-error: true', text)
            self.assertNotIn('gh pr merge', text)
            self.assertNotIn('persist-credentials: true', text)
            self.assertNotIn('MAINTENANCE_HELPER: ${{ runner.temp }}', text)


if __name__ == '__main__':
    unittest.main()

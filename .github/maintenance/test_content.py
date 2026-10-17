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

    def test_content_ci_is_read_only_and_has_no_provider_calls(self):
        root = Path(__file__).parents[1]
        paths = sorted((root / 'workflows').glob('*.yml'))
        self.assertEqual([path.name for path in paths], ['content-ci.yml'])
        workflow = paths[0].read_text()
        data = c.guard.yaml.load(workflow, Loader=c.guard.WorkflowLoader)
        branches = {'BFS-Projects': 'development', 'javascript-solutions': 'main', 'tutorials-files': 'master'}
        self.assertEqual(set(data['on']), {'pull_request', 'push', 'workflow_dispatch'})
        self.assertEqual(data['on']['push']['branches'], [branches[c.profile()]])
        self.assertEqual(data['permissions'], {'contents': 'read'})
        self.assertEqual(set(data['jobs']), {'validate'})
        for forbidden in ['OPENAI_API_KEY', 'aider', 'gh pr', 'gh issue', 'contents: write', 'persist-credentials: true', 'continue-on-error: true']:
            self.assertNotIn(forbidden, workflow)


if __name__ == '__main__':
    unittest.main()

# Content and tutorial maintenance

Both original daily schedules are preserved. The factory triages failing pull
requests into deduplicated investigation issues. Daily maintenance runs meaningful
repository-specific checks before any AI call. Neither workflow merges PRs.

- BFS-Projects: README structure, local link targets, JSON and workflow syntax
- javascript-solutions: those checks plus every root extensionless JavaScript
  snippet parsed with Node, including filenames with spaces, and focused regression tests
- tutorials-files: those checks plus tracked JavaScript syntax, focused regression
  tests, and the actual nested client-side-storage-api-handling TypeScript/Vite build

Root npm commands are not applicable. The tutorial's nested project has no lockfile;
its manifest is installed with scripts disabled and no lockfile writes in a temporary
copy. Dependency resolution is therefore not reproducible. External link availability,
HTML/browser behavior, and a complete application test suite are not covered. The
workflow reports these limits; actual validation failures fail the run.

Automatic source/dependency repair is unsupported because these repositories lack
sufficient comprehensive test coverage. The AI proposal path is **README.md only**;
source snippets and the repository inventory provide read-only context. Manual or
label-triggered issue requests must name README.md and produce documentation proposals,
not claims that code issues were implemented. Unsupported requests are explicitly
reported as skipped. One open documentation/review-required proposal blocks duplicates.

The shared maintenance guard verifies protected file bytes, tracked file sets,
executable modes, Git HEAD and index. It catches provider failures even when aider
exits zero. Missing credentials fail a requested AI attempt. No model calls run for
pull requests or default-branch pushes. Pushes run validation only. Guards and repository checks must pass again before draft publication.
No secrets or access settings are added. Package validation receives no GitHub or
OpenAI environment tokens; checkout credentials are not persisted. These publication
checks are not a sandbox for executing repository code.

Run:

    PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s .github/maintenance -p 'test_*.py'
    bash -n .github/maintenance/content.sh
    PYTHONDONTWRITEBYTECODE=1 python .github/maintenance/content.py validate

Python requires PyYAML==6.0.3; use Node 22 (22.12 or later for the Vite tutorial).
Generated drafts still require human review and exact-head CI. GITHUB_TOKEN events
may require a maintainer to approve workflow runs. A draft is not a claim that remote
CI passed or that an AI provider has available credit.

# Content validation

Content CI runs on pull requests, pushes to the default branch, and manual dispatch.
It has read-only repository access and does not make model calls or publish changes.

- BFS-Projects: README structure, local link targets, JSON and workflow syntax
- javascript-solutions: those checks plus every root extensionless JavaScript
  snippet parsed with Node, including filenames with spaces, and focused regression tests
- tutorials-files: those checks plus tracked JavaScript syntax, focused regression
  tests, and the nested client-side-storage-api-handling TypeScript/Vite build

Root npm commands are not applicable. The tutorial's nested project has no lockfile;
its manifest is installed with scripts disabled and no lockfile writes in a temporary
copy. Dependency resolution is therefore not reproducible. External link availability,
HTML/browser behavior, and a complete application test suite are not covered.
Actual validation failures fail the run.

Run:

    PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s .github/maintenance -p 'test_*.py'
    PYTHONDONTWRITEBYTECODE=1 python .github/maintenance/content.py validate

Python requires PyYAML==6.0.3; use Node 22 (22.12 or later for the Vite tutorial).
Use `content.py syntax` when intentionally skipping the nested tutorial build.

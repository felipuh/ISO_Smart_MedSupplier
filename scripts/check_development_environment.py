"""Read-only verification of an independent, pinned development interpreter.

Run with .venv-development/bin/python. Never imports application settings.
"""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / '.venv-development'
if Path(sys.prefix).resolve() != EXPECTED.resolve() or sys.prefix == sys.base_prefix:
    raise SystemExit('Use this product .venv-development/bin/python')
lock = next((ROOT / 'backend' / name for name in (
    'requirements-development.lock', 'requirements-staging.lock')
    if (ROOT / 'backend' / name).is_file()))
normalize = lambda value: re.sub(r'[-_.]+', '-', value).lower()
expected = {normalize(name): version for name, version in re.findall(
    r'^([A-Za-z0-9_.-]+)==([^\s\\]+)', lock.read_text(), re.MULTILINE)}
installed = {normalize(d.metadata['Name']): d.version for d in metadata.distributions()}
errors = [name for name, version in expected.items() if installed.get(name) != version]
for distribution in metadata.distributions():
    if not Path(distribution.locate_file('')).resolve().is_relative_to(EXPECTED.resolve()):
        errors.append('package outside independent environment')
for config in EXPECTED.glob('lib/python*/site-packages/*.pth'):
    for line in config.read_text().splitlines():
        if line.strip() and not line.startswith(('#', 'import ')):
            if not (config.parent / line).resolve().is_relative_to(EXPECTED.resolve()):
                errors.append('external package path')
if errors:
    raise SystemExit('Environment mismatch: ' + ', '.join(sorted(set(errors))))
print(json.dumps({'status': 'PASS', 'python': sys.version.split()[0],
    'product': ROOT.name, 'prefix': str(EXPECTED), 'locked_packages': len(expected),
    'django': installed['django'], 'lock_sha256': hashlib.sha256(lock.read_bytes()).hexdigest(),
    'application_settings_loaded': False}, indent=2))

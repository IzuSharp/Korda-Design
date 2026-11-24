#!/usr/bin/env python3
"""Check current DB names without rewriting accepted historical contracts."""
from pathlib import Path
import copy
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FROZEN = 'fcc2b3599066a467ce3d8bf52e4753bdeea6cd86'
SUFFIXES = ('Table', 'Column', 'Key', 'Version', 'Ignore', 'Projection',
            'Constructor', 'Parameter', 'Codec', 'UseCodec')
CURRENT = [
    'docs/api/README.md', 'docs/api/database.md', 'docs/api/getting-started.md',
    'docs/api/documentation-system.md', 'docs/database/current-product.md',
    'docs/platforms/support-and-aot.md', 'docs/verification/models-and-matrix.md',
    'templates/public-api/AGENTS.fragment.md', 'templates/public-api/adoption-checklist.md',
    'docs/api/guides.md', 'docs/api/nuget-and-consumption.md', 'docs/api/reference.md',
    'docs/database/fluent-orm.md', 'docs/generators/query-generation.md',
    'docs/standards/csharp-public-api-and-documentation.md',
]


def validate(data):
    assert data['schema_version'] == 1 and data['task'] == 'DB-Rename-01'
    assert data['branch'] == 'task/DB-Rename-01-linux' and data['baseline'] == FROZEN
    assert data['namespace'] == 'Korda.Data'
    assert data['mappings'] == {f'Weave{x}Attribute': f'Db{x}Attribute' for x in SUFFIXES}
    assert data['preserved'] == ['namespace', 'constructor_parameters', 'defaults',
                                 'attribute_targets', 'behavior', 'json_source_generation',
                                 'native_abi', 'persisted_database_identifiers']
    assert data['compatibility'] == 'source_and_binary_break_recompile_consumers'
    assert all(data[key] is False for key in
               ('aliases', 'merge_authorized', 'publication_authorized', 'product_execution_claimed'))


def main():
    data = json.loads((ROOT / 'docs/database/db-attribute-names.json').read_text())
    validate(data)
    protected = ['docs/contracts', 'docs/history', 'docs/traceability', 'docs/research',
                 'verification', 'experiments', 'docs/current-scope.json',
                 'docs/api/*.json', 'docs/database/cpp-migration.json',
                 'docs/database/cpp-migration.md', 'docs/database/fluent-orm.json',
                 'docs/decisions', 'tools/verify_fluent_orm.py', 'tools/verify_cpp_migration.py',
                 'tools/verify_db_scope.py', 'tools/verify_db_scope_history.py']
    changed = subprocess.check_output(['git', 'diff', '--name-only', FROZEN, '--', *protected],
                                      cwd=ROOT, text=True)
    assert not changed.strip(), 'Historical accepted content changed: ' + changed
    old_name = re.compile(r'\bWeave(?:' + '|'.join(SUFFIXES) + r')(?:Attribute)?\b')
    for name in CURRENT:
        content = (ROOT / name).read_text()
        assert not old_name.search(content), 'Old current attribute: ' + name
        assert not re.search(r'\bNativeWeave\.(?:Data|Database|Query)\b', content), name
    for name in [*CURRENT, 'AGENTS.md', 'CURRENT-PHASE.md', 'README.md',
                 'docs/database/db-attribute-names.md',
                 'docs/platforms/build-package-release.md', 'docs/requirements/coverage-matrix.md']:
        path = ROOT / name
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            assert (path.parent / target.split('#', 1)[0]).exists(), 'Broken link: ' + target
    for name in ('docs/platforms/build-package-release.md', 'docs/requirements/coverage-matrix.md'):
        assert (ROOT / name).read_text().startswith('# Historical DB-Scope-01 '), name
    invalid = []
    bad = copy.deepcopy(data); bad['mappings'].pop('WeaveTableAttribute'); invalid.append(bad)
    bad = copy.deepcopy(data); bad['namespace'] = 'Db'; invalid.append(bad)
    bad = copy.deepcopy(data); bad['aliases'] = True; invalid.append(bad)
    bad = copy.deepcopy(data); bad['publication_authorized'] = True; invalid.append(bad)
    bad = copy.deepcopy(data); bad['product_execution_claimed'] = True; invalid.append(bad)
    for bad in invalid:
        try:
            validate(bad)
        except AssertionError:
            continue
        raise AssertionError('Invalid naming contract accepted')
    with tempfile.TemporaryDirectory(prefix='db-rename-history-', dir=ROOT.parent) as temp:
        work = Path(temp) / 'NativeWeave-Design'
        subprocess.run(['git', 'worktree', 'add', '--detach', str(work), FROZEN], cwd=ROOT, check=True)
        try:
            subprocess.run(['python3', 'tools/verify_fluent_orm.py'], cwd=work, check=True)
        finally:
            subprocess.run(['git', 'worktree', 'remove', '--force', str(work)], cwd=ROOT, check=True)
    print(json.dumps({'task': 'DB-Rename-01', 'naming_contract': 'passed',
                      'negative_controls': len(invalid), 'history': 'passed_at_immutable_input',
                      'product_execution_claimed': False}, indent=2))


if __name__ == '__main__':
    main()

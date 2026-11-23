#!/usr/bin/env python3
"""Validate DB-API-01 contracts and run unchanged historical migration gates."""
from pathlib import Path
import argparse
import copy
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FROZEN = 'de1f4796dc199250b405ea99f2129d611f17b1f6'
PLAN_FIRST = '21e98f7591b4cf1f7fd5b7d5e791ab0be4271515'
OPERATIONS = {'model-conventions', 'projection', 'value-policies', 'query-composition',
              'composite-cursor', 'batched-relations', 'writes', 'transaction-callback',
              'migration-draft', 'reverse-scaffold', 'onboarding'}
CHECKS = {'model_projection', 'reusable_mappings', 'query_composition', 'cursor_relations',
          'writes_concurrency', 'transaction_outcomes', 'onboarding', 'migrations_scaffold',
          'api_compatibility', 'postgresql_aot', 'sqlite_aot', 'native_reuse'}


def validate(data):
    assert data['schema_version'] == 1 and data['task'] == 'DB-API-01'
    assert data['branch'] == 'task/DB-API-01-linux' and data['status'] == 'authorized_design'
    assert data['baseline']['NativeWeave-Design'] == FROZEN
    assert data['plan_first'] == {'repository': 'IzuSharp/Plan', 'commit': PLAN_FIRST,
                                 'path': 'ledger/evidence/batches/DB-API-01/plan.md'}
    assert data['platforms'] == ['linux-x64']
    assert data['packages'] == ['Korda.Database.PostgreSql', 'Korda.Database.Sqlite']
    assert data['execution'] == {'native_language': 'C++20', 'postgresql': 'libpq', 'sqlite': 'sqlite3',
                                 'query_owner': 'existing native kernel', 'mapping': 'C# source generation'}
    assert data['consumer_modes'] == ['native-aot']
    assert data['clean_image_requested'] is False and data['cpu_emulation_requested'] is False
    assert data['product_acceptance'] == 'owned_by_plan' and data['current_checks_claim_product_execution'] is False
    assert data['compatibility'] == {'existing_public_api': 'additive unless separately reviewed',
                                    'native_abi': 'preserve old layouts/actions; negotiate additions',
                                    'package_identity': 'existing independent top-level providers',
                                    'dto_native_rebuild': 'not_required'}
    assert len(data['operations']) == len(OPERATIONS)
    assert {row['id'] for row in data['operations']} == OPERATIONS
    covered = set()
    for row in data['operations']:
        assert row['modules'] and len(set(row['modules'])) == len(row['modules'])
        assert all(re.fullmatch(r'(src|native|docs|samples)/[A-Za-z0-9_./-]+/', path) for path in row['modules'])
        assert len(row['mapping'].split(' -> ')) >= 2 and row['boundary'].strip()
        assert row['implementation_status'] in {'pending', 'implemented_evidence_in_plan'}
        assert row['acceptance_checks'] and set(row['acceptance_checks']) <= CHECKS
        covered.update(row['acceptance_checks'])
    assert covered == CHECKS, 'Missing acceptance mapping'
    assert {'real-postgresql-aot', 'real-sqlite-aot', 'external-provider-packagereference',
            'observed-sql-roundtrips', 'dto-change-same-native-hashes', 'exact-pr-checks',
            'observed-merged-main-ci', 'observed-triggered-releases'} <= set(data['evidence_requirements'])
    for path in [data['contract_document'], data['decision']]:
        assert not Path(path).is_absolute() and '..' not in Path(path).parts and (ROOT / path).is_file()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current-only', action='store_true', help='Only for staged local contract checks; normal CI includes history.')
    args = parser.parse_args()
    data = json.loads((ROOT / 'docs/database/fluent-orm.json').read_text())
    validate(data)
    protected = ['docs/contracts', 'docs/traceability/reviews', 'verification', 'experiments',
                 'docs/history', 'docs/current-scope.json', 'docs/database/cpp-migration.json',
                 'docs/database/cpp-migration.md', 'docs/decisions/ADR-0006-database-cpp-native.md',
                 'tools/verify_cpp_migration.py', 'tools/verify_db_scope.py', 'tools/verify_db_scope_history.py']
    changed = subprocess.check_output(['git', 'diff', '--name-only', FROZEN, '--', *protected], cwd=ROOT, text=True)
    assert not changed.strip(), 'Historical accepted content changed: ' + changed
    for relative in ['AGENTS.md', 'CURRENT-PHASE.md', 'README.md', data['contract_document'], data['decision']]:
        path = ROOT / relative
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            assert (path.parent / target.split('#', 1)[0]).exists(), 'Broken link: ' + target
    cases = []
    bad = copy.deepcopy(data); bad['operations'].pop(); cases.append(bad)
    bad = copy.deepcopy(data); bad['operations'][0]['acceptance_checks'] = []; cases.append(bad)
    bad = copy.deepcopy(data); bad['execution']['query_owner'] = 'managed SQL engine'; cases.append(bad)
    bad = copy.deepcopy(data); bad['plan_first']['commit'] = '0' * 40; cases.append(bad)
    bad = copy.deepcopy(data); bad['current_checks_claim_product_execution'] = True; cases.append(bad)
    bad = copy.deepcopy(data); bad['compatibility']['dto_native_rebuild'] = 'required'; cases.append(bad)
    for bad in cases:
        try:
            validate(bad)
        except AssertionError:
            continue
        raise AssertionError('Invalid contract fixture accepted')
    if not args.current_only:
        with tempfile.TemporaryDirectory(prefix='db-api-history-', dir=ROOT.parent) as temp:
            work = Path(temp) / 'NativeWeave-Design'
            subprocess.run(['git', 'worktree', 'add', '--detach', str(work), FROZEN], cwd=ROOT, check=True)
            try:
                subprocess.run(['python3', 'tools/verify_cpp_migration.py'], cwd=work, check=True)
            finally:
                subprocess.run(['git', 'worktree', 'remove', '--force', str(work)], cwd=ROOT, check=True)
    print(json.dumps({'task': 'DB-API-01', 'contract_gate': 'passed', 'negative_controls': len(cases),
                      'history': 'not_run' if args.current_only else 'passed_at_immutable_input',
                      'product_execution_claimed': False}, indent=2))


if __name__ == '__main__':
    main()

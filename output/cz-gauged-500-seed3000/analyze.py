from hashlib import sha256
from itertools import accumulate
import json
from math import comb, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = 500
START = 3000
RATES = dict(two_qubit_infidelity='1/1000', readout_flip_probability='1/1000',
             one_qubit_infidelity='1/10000', t_infidelity='1/10000',
             idle_infidelity='0', preparation_flip_probability='0')
ARMS = [
    ('joint_off', 'Compact13 round trip, joint off', 'parallel-reference/joint-off'),
    ('joint_fallback', 'Compact13 round trip, joint fallback', 'parallel-reference/joint-fallback'),
    ('compact13_short', 'Compact13 shortened votes', 'short-handoff/compact13'),
    ('tree4_two_scans', 'Tree4 shortened votes, two resource scans', 'short-handoff/tree4'),
    ('tree4_block_flags', 'Tree4 shortened votes, block flags', 'tree4-block-flags/tree4'),
    ('cat_dual', 'Cat-dual', 'parallel-reference/cat-dual'),
    ('tuned_cat', 'Tuned five-parity cat', 'tuned-cat/cat-five-parity'),
]


def read(path):
    return json.loads(path.read_text())


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    scale = 1 + z*z/n
    center = (p + z*z/(2*n)) / scale
    radius = z * sqrt(p * (1 - p)/n + z*z/(4*n*n)) / scale
    return [max(0, center - radius), min(1, center + radius)]


def arm(label, folder):
    manifest = folder / 'manifest.json'
    if not manifest.is_file():
        manifest = folder.parent / 'manifest.json'
    meta = read(manifest)
    assert meta['seed'] == START
    assert meta['noise']['rates'] == RATES
    assert meta['noise']['fault_count_cap'] is None
    with (folder / 'shots.jsonl').open() as stream:
        rows = [json.loads(line) for line in stream]
    assert len(rows) == N, folder
    assert [r['shot_index'] for r in rows] == list(range(N)), folder
    assert [r['seed'] for r in rows] == list(range(START, START + N)), folder
    done = [r for r in rows if r['execution_status'] == 'completed']
    accepted = [r for r in done if r['accepted']]
    matches = [r for r in accepted if r.get('diagnostics', {}).get('decoded_target_within_tolerance')]
    s = read(folder / 'summary.json')
    assert (s['attempts'], s['completed'], s['accepted'], s['accepted_within_target_tolerance']) == (
        N, len(done), len(accepted), len(matches)), folder
    if (folder / 'clean-gates.json').is_file():
        gates = read(folder / 'clean-gates.json')
    else:
        key = 'direct_cat/recovery' if folder.name == 'cat-dual' else 'compact13/recovery'
        gates = read(folder / 'clean-costs.json')[key]['gates']
    total = s['total_executed_gates_completed']
    misses = [dict(seed=r['seed'], sampled_faults=r['metrics']['sampled_noise_events'],
                   decoded_fidelity=r.get('diagnostics', {}).get('decoded_target_fidelity'))
              for r in accepted if not r.get('diagnostics', {}).get('decoded_target_within_tolerance')]
    outcome = {r['seed']:r['accepted'] for r in done}
    data = dict(label=label, attempts=N, accepted=len(accepted), rejected=len(done)-len(accepted),
                unresolved=N-len(done), matches=len(matches), acceptance_interval=wilson(len(accepted), len(done)),
                clean_CX=gates['CX'], clean_T_TDG=gates.get('T',0)+gates.get('TDG',0),
                completed_CX_per_target=total['CX']/len(matches),
                completed_T_TDG_per_target=(total.get('T',0)+total.get('TDG',0))/len(matches),
                nonmatching_accepts=misses, summary=str((folder/'summary.json').relative_to(ROOT)),
                manifest=str(manifest.relative_to(ROOT)),
                shot_log_sha256=sha256((folder/'shots.jsonl').read_bytes()).hexdigest())
    return data, outcome


def paired(a, b, outcomes):
    left, right = outcomes[a], outcomes[b]
    common = left.keys() & right.keys()
    gained = sum(left[s] and not right[s] for s in common)
    lost = sum(right[s] and not left[s] for s in common)
    n = gained + lost
    p = min(1.0, 2 * sum(comb(n, i) for i in range(min(gained, lost)+1)) / (2**n))
    return dict(left=a, right=b, completed_pairs=len(common), left_only_accepted=gained,
                right_only_accepted=lost, difference_percentage_points=100*(gained-lost)/len(common),
                exact_two_sided_p=p)


def verify_reference_overlap():
    counts = {}
    for mode in ('joint-off','joint-fallback','cat-dual'):
        official = ROOT / 'round-trip-and-cat-dual' / mode / 'shots.jsonl'
        if not official.is_file():
            continue
        mirror = ROOT / 'parallel-reference' / mode / 'shots.jsonl'
        a, b = ({r['seed']: r for r in map(json.loads, path.read_text().splitlines())}
                for path in (official, mirror))
        common = a.keys() & b.keys()
        checked = 0
        for seed in common:
            left, right = a[seed], b[seed]
            if left['execution_status'] != 'completed' or right['execution_status'] != 'completed':
                continue
            for key in ('accepted','reason','joint_recovery_episodes'):
                assert left.get(key) == right.get(key), (mode, seed, key)
            for key in ('gate_counts','sampled_noise_events'):
                assert left['metrics'][key] == right['metrics'][key], (mode, seed, key)
            if left['accepted']:
                assert abs(left['diagnostics']['decoded_target_fidelity'] - right['diagnostics']['decoded_target_fidelity']) < 1e-12
            checked += 1
        counts[mode] = checked
    return counts


def main():
    results = {}
    outcomes = {}
    for key, label, path in ARMS:
        results[key], outcomes[key] = arm(label, ROOT / path)
    overlap = verify_reference_overlap()
    comparisons = [paired(a, b, outcomes) for a, b in (
        ('tree4_two_scans','joint_fallback'), ('tree4_two_scans','compact13_short'),
        ('tree4_two_scans','cat_dual'), ('tree4_two_scans','tuned_cat'),
        ('tree4_block_flags','tree4_two_scans'),
        ('tree4_block_flags','joint_fallback'), ('tree4_block_flags','cat_dual'),
        ('tree4_block_flags','tuned_cat'),
    )]
    order = sorted(comparisons, key=lambda c:c['exact_two_sided_p'])
    for row, p in zip(order, accumulate(((len(order)-j)*row['exact_two_sided_p'] for j,row in enumerate(order)), max)):
        row['holm_adjusted_p'] = min(1, p)
    table = [
        '# 500-shot gauged-CZ comparison, seed 3000', '',
        'Each arm used attempt seeds 3000–3499 and the previous gate and readout rates. The simulator sampled an unbounded number of faults.', '',
        '| Method | Accepted | Rejected | Unresolved | Acceptance, 95% Wilson interval | Decoded matches | Clean CX / T | Completed CX per match |',
        '|---|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for a in results.values():
        lo, hi = a['acceptance_interval']
        rate = a['accepted'] / (N - a['unresolved'])
        table.append(f"| [{a['label']}]({a['summary']}) | {a['accepted']} / {N} | {a['rejected']} | {a['unresolved']} | {rate:.1%} ({lo:.1%}–{hi:.1%}) | {a['matches']} | {a['clean_CX']:,} / {a['clean_T_TDG']} | {a['completed_CX_per_target']:,.1f} |")
    table += ['', 'Wilson intervals use completed attempts. CX per match includes the cost of completed rejections.', '',
              '## Same-seed comparisons', '',
              '| Comparison | Left-only accepts | Right-only accepts | Acceptance difference | Adjusted p |',
              '|---|---:|---:|---:|---:|']
    for c in comparisons:
        left, right = (results[c[which]]['label'] for which in ('left','right'))
        table.append(f"| {left} vs. {right} | {c['left_only_accepted']} | {c['right_only_accepted']} | {c['difference_percentage_points']:+.1f} pp | {c['holm_adjusted_p']:.4g} |")
    table += ['', 'The two-sided exact McNemar tests compare acceptance by attempt seed. A common seed does not imply an identical physical trajectory across circuits. Holm adjustment accounts for all eight comparisons, including the supplementary block-flag comparisons.']
    table += ['', 'The reference arms use the unchanged simulator in persistent parallel workers. Cross-check counts against the original harness are recorded in the comparison JSON.']
    (ROOT/'comparison.md').write_text('\n'.join(table)+'\n')
    (ROOT/'comparison.json').write_text(json.dumps(dict(seed=START, attempts_per_arm=N, noise_rates=RATES,
                                                       arms=results, paired_comparisons=comparisons, reference_overlap=overlap), indent=2)+'\n')
    print('\n'.join(table))


if __name__ == '__main__':
    main()

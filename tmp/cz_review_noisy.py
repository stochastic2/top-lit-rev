"""Scratch noisy pilot for the single-block CZ review variants."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src' / name) for name in ('single_block_cz', 'shared', 'two_block_swap')]

from run_single_block_cz_controller import RecordBackend, Reject
from simulate_single_block_cz_cat_depolarizing import CatStateController
from simulate_single_block_cz_depolarizing import noise_seed, summarize, write_json
from single_cz_controller import SimulationController
from single_cz_diagnostics import diagnose
from single_cz_persistent import TREE4, fused_initial_program
from single_cz_runtime import NoiseModel, QuantumBackend


class TreeFirstVote(SimulationController):
    def graph(self):
        edges = self.graph_choice.edges
        vertices = [f'a{v}' for v in range(5)]
        links = [f'A{e}' for e in range(len(edges))]
        while True:
            self.context('graph/raw')
            for vertex in vertices:
                self.prep(vertex)
                self.gate('H', vertex)
            for link in links:
                self.prep(link)
            for link, (u, v) in zip(links, edges):
                self.gate('CX', vertices[u], link)
                self.gate('CX', vertices[v], link)
            self.b.boundary()
            self.context('graph/parity')
            reports = []
            for link, (u, v) in zip(links, edges):
                self.prep('w')
                for target in (vertices[u], link, vertices[v]):
                    self.gate('CX', target, 'w')
                reports.append(self.mz('w'))
            self.record.append({'graph_parity_reports': reports})
            self.b.boundary()
            if not any(reports):
                return
            self.dispose(vertices + links)
            self.retry('known_unused_graph_parity')

    def gauging_persistent(self):
        self.graph()
        self.context('persistent/fused_initial')
        for op, targets in fused_initial_program(self.graph_choice):
            self.gate(op, *targets)
        self.context('vertex_readout')
        reports = []
        for v in range(5):
            role = f'a{v}'
            self.gate('H', role)
            reports.append(self.mz(role))
        passed = int(sum(reports) % 2 == 0)
        self.record.append({'vertex_reports': reports, 'passes': passed})
        self.context('persistent/discard_graph')
        self.dispose([f'A{e}' for e in range(len(self.graph_choice.edges))])
        self.b.boundary()

        ports = [('W', f'D{q}') for q in range(20)]
        for r in range(4):
            prefix = f'persistent/{r}'
            syndrome = self.code(prefix + '/code')
            if any(syndrome):
                self.data_recover(prefix + '/data_recovery', syndrome)
            passed += self.check(prefix + '/U', ports) == 0
            self.record.append({'confirmation_round': r, 'passes': passed})
            self.b.boundary()
            if passed == 3:
                return
            if passed + (3 - r) < 3:
                raise Reject('insufficient_votes')


class SourceAsFirstVote:
    def code(self, prefix, *args, **kwargs):
        if prefix == 'terminal/0':
            return [0] * 18
        return super().code(prefix, *args, **kwargs)


class DirectFirstVote(SourceAsFirstVote, SimulationController):
    pass


class FiveParityCat(SourceAsFirstVote, CatStateController):
    def cat(self, size, name):
        if size != 20:
            return super().cat(size, name)
        leaves = [f'L{q}' for q in range(size)]
        for leaf in leaves:
            self.prep(leaf)
        self.gate('H', leaves[0])
        for control, target in zip(leaves, leaves[1:]):
            self.gate('CX', control, target)

        def scan(checks):
            bits = []
            for support in checks:
                self.prep('w')
                for q in support:
                    self.gate('CX', leaves[q], 'w')
                bits.append(self.mz('w'))
            return bits

        checks = ((0, 2, 4, 6, 8, 10, 12, 16), (0, 5, 9, 13, 15, 18),
                  (1, 11, 17, 19), (3, 14), (7, 19))
        fast = scan(checks)
        self.record.append({'cat': name, 'five_parity_reports': fast})
        if not any(fast):
            return leaves

        # A nonzero parity report spends at least one fault. Two equal
        # fresh QND chain records therefore include a clean occurrence.
        chain = [(q, q + 1) for q in range(size - 1)]
        rows = []
        for _ in range(4):
            rows.append(scan(chain))
            if len(rows) >= 2 and rows[-1] == rows[-2]:
                break
        else:
            raise Reject('unstable_five_parity_cat_fallback')
        self.record.append({'cat_fallback': name, 'records': rows})
        bit = 0
        for q, parity in enumerate(rows[-1], 1):
            bit ^= parity
            if bit:
                self.gate('X', leaves[q])
        return leaves


TREE = {'graph': TREE4, 'gauss_frame': 'persistent', 'graph_stars': 'bare',
        'terminal_policy': 'intrinsic', 'graph_z_corrections': 'frame'}
DIRECT = {'route': 'direct_cat'}
ARMS = {
    'tree4-current': (SimulationController, TREE),
    'tree4-first-vote': (TreeFirstVote, TREE),
    'cat-current': (CatStateController, DIRECT),
    'cat-five-parity': (FiveParityCat, DIRECT),
    'direct-first-vote': (DirectFirstVote, DIRECT),
}
MATCHED = {'source_extraction': 'decoded_flags', 'data_checks': 'compact_flags',
           'flag_recovery': 'data', 'conditional_checks': 'dual_flags'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shots', type=int, default=200, help='Attempts per arm')
    parser.add_argument('--seed', type=int, default=2000)
    parser.add_argument('--arms', nargs='+', choices=ARMS, default=list(ARMS))
    parser.add_argument('--output-dir', type=Path, required=True)
    defaults = {'two_qubit_infidelity': '1e-3', 'readout_flip_probability': '1e-3',
                'one_qubit_infidelity': '1e-4', 't_infidelity': '1e-4',
                'idle_infidelity': '0', 'preparation_flip_probability': '0'}
    for name, value in defaults.items():
        parser.add_argument('--' + name.replace('_', '-'), default=value)
    args = parser.parse_args()
    if args.shots < 1 or len(set(args.arms)) != len(args.arms):
        parser.error('Use a positive shot count and distinct arms')
    model = NoiseModel(**{name: getattr(args, name) for name in defaults})
    args.output_dir.mkdir(parents=True, exist_ok=False)
    write_json(args.output_dir / 'manifest.json', {
        'arms': args.arms, 'shots_per_arm': args.shots, 'seed': args.seed, 'noise': model.manifest(),
    })

    for arm in args.arms:
        controller, options = ARMS[arm]
        folder = args.output_dir / arm
        folder.mkdir()
        recorder = RecordBackend()
        assert controller(recorder, **MATCHED, **options).run()['accepted']
        clean = Counter(op for op, _ in recorder.ops)
        write_json(folder / 'clean-gates.json', clean)
        print(f'{arm} clean CX = {clean["CX"]}', flush=True)
        records = []
        with (folder / 'shots.jsonl').open('x') as stream:
            for index in range(args.shots):
                seed = args.seed + index
                backend = QuantumBackend(seed=seed, noise_seed=noise_seed(seed), model=model)
                row = {'shot_index': index, 'seed': seed, 'execution_status': 'completed'}
                try:
                    result = controller(backend, **MATCHED, **options).run()
                    row.update(accepted=result['accepted'], reason=result.get('reason'))
                    row['metrics'] = backend.metrics()
                    if result['accepted']:
                        diagnostics = diagnose(*backend.state.sparse_output(backend.data_labels))
                        row.update(diagnostics=diagnostics, diagnostic_status='completed')
                        if not diagnostics['decoded_target_within_tolerance']:
                            row.update(controller_record=result['record'], noise_events=backend.noise_events)
                except MemoryError as error:
                    row.update(execution_status='unresolved', failure_kind='capacity', detail=str(error))
                records.append(row)
                stream.write(json.dumps(row) + '\n')
                stream.flush()
                if (index + 1) % 10 == 0 or index + 1 == args.shots:
                    summary = summarize(records)
                    write_json(folder / 'summary.json', summary)
                    print(f"{arm} {summary['accepted']} accepted / {index + 1} attempts, "
                          f"{summary['accepted_within_target_tolerance']} decoded matches, "
                          f"{summary['unresolved']} unresolved", flush=True)


if __name__ == '__main__':
    main()

"""Run the existing reference controllers in parallel for the 500-shot comparison."""

from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
import multiprocessing
from pathlib import Path
import signal
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT/'src'/d) for d in ('single_block_cz','shared','two_block_swap')]

from simulate_single_block_cz_depolarizing import clean_costs, simulate, summarize, write_json
from single_cz_diagnostics import diagnose
from single_cz_runtime import NoiseModel

RATES = dict(two_qubit_infidelity='1e-3', readout_flip_probability='1e-3',
             one_qubit_infidelity='1e-4', t_infidelity='1e-4',
             idle_infidelity='0', preparation_flip_probability='0')
COMMON = dict(graph='compact13', profile='recovery', history_policy='triple',
              source_extraction='decoded_flags', flag_recovery='data',
              max_flag_recoveries=8, data_checks='compact_flags', gauss_frame='round_trip',
              graph_z_corrections='physical', conditional_checks='dual_flags')
JOINT = dict(route='gauging', graph_stars='bare', terminal_policy='screen', root_recovery='joint')
CAT = dict(route='direct_cat', direct_cz_extraction='cat', graph_stars='flags', terminal_policy='certified')
FIRST_SEED = 3000
SHOTS = 500
TIMEOUT = 120


def deadline(*_):
    raise TimeoutError('reference worker deadline')


def run(shot_index, mode):
    seed = FIRST_SEED + shot_index
    options = CAT if mode == 'cat-dual' else (JOINT | {'joint_recovery': mode.removeprefix('joint-')})
    signal.alarm(TIMEOUT)
    try:
        result, backend = simulate(seed=seed, model=NoiseModel(**RATES), **COMMON, **options)
        record = result.pop('record')
        result.update(execution_status='completed', shot_index=shot_index,
                      diagnostic_status='not_applicable')
        if result['accepted']:
            result['diagnostics'] = diagnose(*backend.state.sparse_output(backend.data_labels))
            result['diagnostic_status'] = 'completed'
            if not result['diagnostics']['decoded_target_within_tolerance']:
                result.update(controller_record=record, noise_events=backend.noise_events)
        return result
    except (TimeoutError, MemoryError, ArithmeticError) as exc:
        return dict(seed=seed, shot_index=shot_index, execution_status='unresolved',
                    failure_kind=type(exc).__name__, detail=str(exc))
    finally:
        signal.alarm(0)


def trial(request):
    signal.signal(signal.SIGALRM, deadline)
    shot_index, mode = request
    result = run(shot_index, mode)
    if mode == 'cat-dual':
        return {mode: result}
    # The legacy controller branches on the fallback switch only in
    # apply_data_reference. Every such invocation charges an episode.
    if result['execution_status'] == 'completed' and result['joint_recovery_episodes'] == 0:
        off = result | {'joint_recovery': 'off', 'reused_identical_nonfallback_trajectory': True}
    else:
        off = run(shot_index, 'joint-off')
    return {mode:result, 'joint-off':off}


def main(workers):
    directory = HERE/'parallel-reference'
    directory.mkdir(exist_ok=False)
    modes = ('joint-off','joint-fallback','cat-dual')
    rows = {mode:[] for mode in modes}
    for mode in modes:
        folder = directory/mode
        folder.mkdir()
        cat = mode == 'cat-dual'
        options = CAT if cat else (JOINT | {'joint_recovery': mode.removeprefix('joint-')})
        kwargs = {k:v for k,v in (COMMON | options).items() if k in {
            'source_extraction','flag_recovery','data_checks','gauss_frame','graph_z_corrections',
            'conditional_checks','direct_cz_extraction','graph_stars','terminal_policy',
            'root_recovery','joint_recovery'}}
        write_json(folder/'clean-costs.json', clean_costs(**kwargs))
        write_json(folder/'manifest.json', dict(seed=FIRST_SEED, shots_requested=SHOTS, noise=NoiseModel(**RATES).manifest(),
                   simulator_options=COMMON | options, timeout_seconds=TIMEOUT,
                   runner='in-process reuse of existing simulate() with persistent worker cache',
                   runner_sha256=sha256(Path(__file__).read_bytes()).hexdigest()))
    requests = [(j, mode) for j in range(SHOTS) for mode in ('joint-fallback','cat-dual')]
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        for output in pool.map(trial, requests):
            for mode, row in output.items():
                rows[mode].append(row)
                folder = directory/mode
                with (folder/'shots.jsonl').open('a') as stream:
                    stream.write(json.dumps(row)+'\n')
                if len(rows[mode]) % 25 == 0:
                    summary = summarize(rows[mode])
                    write_json(folder/'summary.json', summary)
                    print(mode, summary['accepted'], '/', len(rows[mode]), 'unresolved', summary['unresolved'], flush=True)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv)>1 else 6)

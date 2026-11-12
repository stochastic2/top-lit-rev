# Matched-run fidelity analysis

Read [report.md](report.md) for the table and uncertainty bounds,
[analysis.json](analysis.json) for all statistics and the recorded failure,
and [replay.json](replay.json) for the deterministic counterfactual checks.
All 190 accepted output kets were reloaded and independently diagnosed.
Saved report/control certificates, common settings and runtime hashes match.
Original benchmark attempts and summaries were not modified.

The only accepted mismatch is `cat-cats`, shot 27, seed 1027:

- Its decoded state is |11>, orthogonal to CZ magic. Mean fidelity of that
  configuration is 79/80=98.75%, not 80 slightly imperfect magic states.
- Round 0 has actual cat-leaf parity 1 (negative), but L13's report flips.
- Round 1 again has negative actual parity, but L3's report flips.
- Round 2 has a Z_L7 Z_w fault on a cat-verification CX. It leaves all ZZ
  reports zero while flipping the cat phase; its positive leaf parity
  therefore falsely certifies the negative data sector.

The original record has five faults. Replaying all five against the exact
saved runtime reproduces every actual/reported measurement and final ket
(overlap one to conversion tolerance). Removing the other two faults
still gives an accepted negative output using the three certificate faults.
Removing any one of those three faults makes the constructed run reject.
This is compatible with the global two-fault accepted-output theorem.
It is one case study, not an exhaustive fault audit.

The same three-cat-sign failure mechanism is possible in `cat-flags`:
changing ordinary code checks does not verify the CZ cat's logical phase.
Zero failures among 45 accepted outputs does not establish immunity.
No intrinsic fidelity advantage of gauging is established by zero failures
among its 52 or 13 accepted outputs either. The exact one-sided 95% upper
target-mismatch probabilities are 5.79%, 6.44%, 5.60%, 20.58% for
cat-cats, cat-flags, gauging-cats, gauging-flags respectively.

Cat-cats has the highest observed acceptance; cat-flags has the lowest
observed CNOT cost per accepted output. T/T† costs differ and were noiseless
in this run. Neither a population-fidelity ranking nor matched-fidelity
hardware advantage follows from this sample.

Reproduce the statistics, choosing a new analysis directory:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/analyze_single_cz_fidelity.py \
  output/cz-matched-20261105-172605 \
  --output-dir output/cz-matched-20261105-172605/fidelity-analysis-repeat
```

Reproduce the failure and two-fault subset checks:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/replay_single_cz_cat_failure.py \
  output/cz-matched-20261105-172605/cat-cats --shot 27 \
  --output output/cz-matched-20261105-172605/fidelity-analysis/replay.json
```

The replay helper imports the hashed runtime snapshot, uses zero stochastic
noise with explicit fault injections, and holds the Born seed fixed.
These replays are not new independent benchmark samples and are not pooled
into the statistical table. The confidence bounds are per-arm binomial
bounds for target mismatch at diagnostic tolerance, not a claim that all
possible quantum infidelities are binary. Shared seeds couple protocols;
no independent-sample significance test or automatic winner is inferred.

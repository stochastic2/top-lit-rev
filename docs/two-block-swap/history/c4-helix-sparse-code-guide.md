# Reading the noiseless sparse C4-Helix simulator

This note follows [`simulate_c4_helix_sparse.py`](../src/simulate_c4_helix_sparse.py) and its backend, [`sparse_wavefunction.py`](../src/sparse_wavefunction.py). It explains the default **noiseless** circuit. The separate gadget simulator has a different state representation and is not covered here. The physical procedure is described in [Full Procedure Integrated V2](full_procedure_integrated_v2.md); the early-gauge-measurement argument is in [Exact Simulation Plan V2](c4-helix-exact-simulation-plan-v2.md).

The simulator follows one measurement history at a time. Between measurements, it keeps every nonzero amplitude of the state conditioned on that history. A measurement samples one outcome using the Born probabilities, and the next state retains every nonzero amplitude compatible with that outcome. In particular, the simulator does not sample one basis string at each gate.

## 1. How a state is stored

### `SparseState`, `__post_init__`, `validate`, `norm_squared`

**Source: `src/sparse_wavefunction.py` — `SparseState.__post_init__`**

```python
    def __post_init__(self) -> None:
        if len(set(self.labels)) != len(self.labels):
            raise ValueError("Quantum coordinate labels must be unique")
        if not self.weights:
            raise ValueError("A normalized state cannot have zero support")
```

**Source: `src/sparse_wavefunction.py` — `SparseState.validate`**

```python
    def validate(self) -> None:
        for key, weight in self.weights.items():
            if len(key) != len(self.labels) or any(bit not in "01" for bit in key):
                raise ValueError(f"Invalid basis key: {key!r}")
            if type(weight) is not int or weight == 0:
                raise ValueError("Weights must be nonzero Python integers")
```

**Source: `src/sparse_wavefunction.py` — `SparseState.norm_squared`**

```python
    def norm_squared(self) -> int:
        """N = sum_x w(x)^2, the norm of the unnormalized integer vector."""
        return sum(weight * weight for weight in self.weights.values())
```


If the named qubits are `labels = (q0, ..., q[n-1])`, the dictionary `weights` stores an integer \(w(x)\) for each nonzero bit string \(x=x_0\cdots x_{n-1}\). It represents the normalized state

\[
|\psi\rangle=\frac{1}{\sqrt{N}}\sum_x w(x)|x\rangle,
\qquad N=\sum_x w(x)^2.
\]

Missing keys have weight zero. For example, `{'00': 1, '11': 1}` represents \((|00\rangle+|11\rangle)/\sqrt2\). The integer \(N\), returned by `norm_squared`, is the squared norm of the **unnormalized integer vector**, not the norm of the physical normalized state. Multiplying every weight by the same nonzero integer, including changing all signs, does not change the physical state.

`__post_init__` requires unique labels and a nonempty dictionary. `validate` additionally checks that each key is a bit string of the right length and each weight is a nonzero Python integer. The implementation uses real integer weights, which suffice for this circuit; it is not a general complex-amplitude simulator.

### `zeros`, `_positions`, `_add_weight`, `_exchange_characters`

**Source: `src/sparse_wavefunction.py` — `SparseState.zeros`**

```python
    @classmethod
    def zeros(cls, labels: Sequence[str]) -> SparseState:
        return cls(tuple(labels), {"0" * len(labels): 1})
```

**Source: `src/sparse_wavefunction.py` — `SparseState._positions`**

```python
    def _positions(self, *labels: str) -> tuple[int, ...]:
        if len(set(labels)) != len(labels):
            raise ValueError("Gate coordinates must be distinct")
        return tuple(self.labels.index(label) for label in labels)
```

**Source: `src/sparse_wavefunction.py` — `_add_weight`**

```python
def _add_weight(output: dict[str, int], key: str, contribution: int) -> None:
    """Add amplitudes at a colliding key, including exact cancellation."""
    total = output.get(key, 0) + contribution
    if total:
        output[key] = total
    else:
        output.pop(key, None)
```

**Source: `src/sparse_wavefunction.py` — `_exchange_characters`**

```python
def _exchange_characters(key: str, left: int, right: int) -> str:
    if left > right:
        left, right = right, left
    if key[left] == key[right]:
        return key
    return key[:left] + key[right] + key[left + 1:right] + key[left] + key[right + 1:]
```


`zeros` constructs \(|0\rangle^{\otimes n}\), with the single entry `{'00...0': 1}`. `_positions` maps qubit labels to their positions and requires distinct gate operands.

`_add_weight` combines contributions to the same output string:

\[
w_{\rm out}(y)\leftarrow w_{\rm out}(y)+c.
\]

If the sum is zero, it removes the key. This is how destructive interference is represented. `_exchange_characters` swaps two bits of a string; it is used by SWAP and controlled SWAP.

## 2. Gates in `sparse_wavefunction.py`

All gates below act on **every stored string**. None samples a string.

### `hadamard`

**Source: `src/sparse_wavefunction.py` — `SparseState.hadamard`**

```python
    def hadamard(self, label: str) -> SparseState:
        """Apply H with a common sqrt(2) factor absorbed in normalization.

        For old bit z and weight c: add c to the bit-0 output and (-1)^z c
        to the bit-1 output. Thus w' = sqrt(2) H w and N(w') = 2 N(w).
        Only use this expansion on small sources. Use measure_x on vertices.
        """
        (q,) = self._positions(label)
        output: dict[str, int] = {}
        for key, weight in self.weights.items():
            _add_weight(output, key[:q] + "0" + key[q + 1:], weight)
            sign = 1 if key[q] == "0" else -1
            _add_weight(output, key[:q] + "1" + key[q + 1:], sign * weight)
        return SparseState(self.labels, output)
```


For the selected bit \(z\), the physical gate is

\[
H|z\rangle=\frac{|0\rangle+(-1)^z|1\rangle}{\sqrt2}.
\]

For each old weight \(c\), the code adds \(c\) to the output with bit 0 and \((-1)^z c\) to the output with bit 1. It absorbs the common \(1/\sqrt2\) into normalization: the integer output represents \(\sqrt2 H w\), and its squared integer norm is \(2N\). `_add_weight` combines contributions when they meet. This expansion is used for the small source preparations.

### `cnot`, `toffoli`, `swap`, `fredkin`

**Source: `src/sparse_wavefunction.py` — `SparseState.cnot`**

```python
    def cnot(self, control: str, target: str) -> SparseState:
        """CX|c,t> = |c,t+c mod 2>; a bijective permutation of keys."""
        c, t = self._positions(control, target)
        output = {}
        for key, weight in self.weights.items():
            if key[c] == "1":
                replacement = "1" if key[t] == "0" else "0"
                key = key[:t] + replacement + key[t + 1:]
            output[key] = weight  # Bijective: distinct inputs cannot collide.
        return SparseState(self.labels, output)
```

**Source: `src/sparse_wavefunction.py` — `SparseState.toffoli`**

```python
    def toffoli(self, control1: str, control2: str, target: str) -> SparseState:
        """CCX, used to independently check the Guppy Fredkin decomposition."""
        c1, c2, t = self._positions(control1, control2, target)
        output = {}
        for key, weight in self.weights.items():
            if key[c1] == key[c2] == "1":
                replacement = "1" if key[t] == "0" else "0"
                key = key[:t] + replacement + key[t + 1:]
            output[key] = weight
        return SparseState(self.labels, output)
```

**Source: `src/sparse_wavefunction.py` — `SparseState.swap`**

```python
    def swap(self, left: str, right: str) -> SparseState:
        """SWAP|l,r> = |r,l>; exchange physical values, not coordinate names."""
        l, r = self._positions(left, right)
        return SparseState(self.labels, {
            _exchange_characters(key, l, r): weight
            for key, weight in self.weights.items()
        })
```

**Source: `src/sparse_wavefunction.py` — `SparseState.fredkin`**

```python
    def fredkin(self, control: str, left: str, right: str) -> SparseState:
        """F|0,l,r>=|0,l,r>, F|1,l,r>=|1,r,l>; both controls stay coherent."""
        c, l, r = self._positions(control, left, right)
        output = {}
        for key, weight in self.weights.items():
            if key[c] == "1":
                key = _exchange_characters(key, l, r)
            output[key] = weight
        return SparseState(self.labels, output)
```


These gates permute basis strings; they keep the corresponding integer weights unchanged. With \(\oplus\) denoting addition modulo 2:

\[
\begin{aligned}
\mathrm{CNOT}:&\quad |c,t\rangle\mapsto|c,t\oplus c\rangle,\\
\mathrm{Toffoli}:&\quad |c_1,c_2,t\rangle\mapsto|c_1,c_2,t\oplus(c_1c_2)\rangle,\\
\mathrm{SWAP}:&\quad |l,r\rangle\mapsto|r,l\rangle,\\
\mathrm{Fredkin}:&\quad |0,l,r\rangle\mapsto|0,l,r\rangle,\qquad
|1,l,r\rangle\mapsto|1,r,l\rangle.
\end{aligned}
\]

The Fredkin gate does not choose a control value: if both control values occur in the state, both are propagated. `toffoli` supports independent checks of the Guppy gate decomposition; the sparse simulator's enrichment uses `fredkin` directly.

### `global_sign`

**Source: `src/sparse_wavefunction.py` — `SparseState.global_sign`**

```python
    def global_sign(self, sign: int) -> SparseState:
        """Retain the explicit +/- sign from gauge-Z feedforward."""
        if sign not in (-1, 1):
            raise ValueError("The global sign must be +1 or -1")
        if sign == 1:
            return self
        return SparseState(self.labels, {key: -value for key, value in self.weights.items()})
```


For \(s\in\{-1,+1\}\), replace every weight \(w(x)\) by \(s w(x)\). This is a global phase on the current trajectory. It explicitly records the effect of the gauge feedforward after conditioning on the gauge word.

## 3. Measurement functions in `sparse_wavefunction.py`

### `sample_binary`

**Source: `src/sparse_wavefunction.py` — `sample_binary`**

```python
def sample_binary(norm_zero: int, norm_one: int, rng: Random) -> int:
    """Draw s with Pr(s) = norm_s / (norm_zero + norm_one), exactly.

    ``randrange`` samples an integer; there is no conversion to float.
    This also handles a deterministic measurement without drawing a number.
    """
    if norm_zero < 0 or norm_one < 0 or norm_zero + norm_one == 0:
        raise ValueError("Measurement norms must be nonnegative with positive sum")
    if norm_zero == 0:
        return 1
    if norm_one == 0:
        return 0
    return int(rng.randrange(norm_zero + norm_one) >= norm_zero)
```


Given nonnegative integers \(N_0,N_1\), with \(N_0+N_1>0\), this function chooses

\[
\Pr(s=0)=\frac{N_0}{N_0+N_1},\qquad
\Pr(s=1)=\frac{N_1}{N_0+N_1}.
\]

It draws a uniformly random integer in \(\{0,\ldots,N_0+N_1-1\}\); the first \(N_0\) possibilities give 0. If one norm is zero the result is deterministic. Integer arithmetic and `Fraction` preserve exact probabilities; the pseudorandom draw chooses a trajectory.

### `_x_pairs`, `x_measurement_norms`, `_select_x`, `project_x`, `measure_x`

**Source: `src/sparse_wavefunction.py` — `SparseState._x_pairs`**

```python
    def _x_pairs(self, q: int) -> Iterator[tuple[str, int, int]]:
        """Visit (remaining key y, a0(y), a1(y)) once, without a large key set.

        A bit-1 key is skipped when its bit-0 partner exists. If its partner
        is absent, the bit-1 key itself owns the pair. Missing weights are zero.
        """
        for key, weight in self.weights.items():
            if key[q] == "0":
                partner = key[:q] + "1" + key[q + 1:]
                yield key[:q] + key[q + 1:], weight, self.weights.get(partner, 0)
            else:
                partner = key[:q] + "0" + key[q + 1:]
                if partner not in self.weights:
                    yield key[:q] + key[q + 1:], 0, weight
```

**Source: `src/sparse_wavefunction.py` — `SparseState.x_measurement_norms`**

```python
    def x_measurement_norms(self, label: str) -> tuple[int, int]:
        """N_b = sum_y (a0(y) + (-1)^b a1(y))^2; N0+N1 = 2N."""
        (q,) = self._positions(label)
        norm_zero = norm_one = 0
        for _, a0, a1 in self._x_pairs(q):
            norm_zero += (a0 + a1) ** 2
            norm_one += (a0 - a1) ** 2
        return norm_zero, norm_one
```

**Source: `src/sparse_wavefunction.py` — `SparseState._select_x`**

```python
    def _select_x(self, label: str, outcome: int) -> SparseState:
        (q,) = self._positions(label)
        sign = 1 if outcome == 0 else -1
        output = {}
        for remaining, a0, a1 in self._x_pairs(q):
            value = a0 + sign * a1
            if value:
                output[remaining] = value
        labels = self.labels[:q] + self.labels[q + 1:]
        return SparseState(labels, output)
```

**Source: `src/sparse_wavefunction.py` — `SparseState.project_x`**

```python
    def project_x(self, label: str, outcome: int) -> tuple[SparseState | None, Fraction]:
        """Select a specified X outcome; return (conditional state, probability).

        <b_X|z> = (-1)^(bz)/sqrt(2), so Pr(b)=N_b/(2N).
        A zero-probability outcome returns (None, 0). No random sampling occurs.
        """
        if outcome not in (0, 1):
            raise ValueError("Measurement outcomes are 0 or 1")
        norms = self.x_measurement_norms(label)
        probability = Fraction(norms[outcome], sum(norms))
        return (self._select_x(label, outcome) if probability else None), probability
```

**Source: `src/sparse_wavefunction.py` — `SparseState.measure_x`**

```python
    def measure_x(self, label: str, rng: Random) -> tuple[SparseState, int, Fraction]:
        """Compute both norms, sample b, then build only the selected dictionary."""
        norms = self.x_measurement_norms(label)
        outcome = sample_binary(*norms, rng)
        return self._select_x(label, outcome), outcome, Fraction(norms[outcome], sum(norms))
```


Let \(z\in\{0,1\}\) be the measured qubit and let \(y\) denote all the remaining bits in their existing order. Write their integer weights as \(w(0,y)\) and \(w(1,y)\), treating missing entries as zero. `_x_pairs` visits each relevant \(y\) once and returns both weights. For outcome \(b=0\) (\(|+\rangle\)) or \(b=1\) (\(|-\rangle\)), define

\[
u_b(y)=w(0,y)+(-1)^b w(1,y),\qquad
N_b=\sum_y u_b(y)^2.
\]

The physical, unnormalized post-measurement vector is

\[
\langle b_X|\psi\rangle=\frac{1}{\sqrt{2N}}\sum_y u_b(y)|y\rangle,
\qquad \Pr(b)=\frac{N_b}{2N},\quad N_0+N_1=2N.
\]

`x_measurement_norms` calculates both \(N_b\). `measure_x` samples one \(b\), and `_select_x` builds **only that outcome's** dictionary, with weights \(u_b(y)\), omitting zero sums. The measured coordinate is removed. Its normalized state is \(\sum_y u_b(y)|y\rangle/\sqrt{N_b}\). Thus the two terms are added or subtracted before probabilities are computed: they are not individually sampled.

`project_x` uses the same calculation but takes a specified outcome instead of sampling it. It returns `None` and probability zero for an impossible outcome.

### `z_measurement_norms`, `_select_z`, `project_z`, `measure_z`

**Source: `src/sparse_wavefunction.py` — `SparseState.z_measurement_norms`**

```python
    def z_measurement_norms(self, label: str) -> tuple[int, int]:
        """N_s = sum_{x: x[q]=s} w(x)^2; N0+N1 = N."""
        (q,) = self._positions(label)
        norms = [0, 0]
        for key, weight in self.weights.items():
            norms[int(key[q])] += weight * weight
        return norms[0], norms[1]
```

**Source: `src/sparse_wavefunction.py` — `SparseState._select_z`**

```python
    def _select_z(self, label: str, outcome: int) -> SparseState:
        (q,) = self._positions(label)
        output = {
            key[:q] + key[q + 1:]: weight
            for key, weight in self.weights.items() if key[q] == str(outcome)
        }
        return SparseState(self.labels[:q] + self.labels[q + 1:], output)
```

**Source: `src/sparse_wavefunction.py` — `SparseState.project_z`**

```python
    def project_z(self, label: str, outcome: int) -> tuple[SparseState | None, Fraction]:
        """Select Z outcome s with Pr(s)=N_s/N; impossible outcomes return None."""
        if outcome not in (0, 1):
            raise ValueError("Measurement outcomes are 0 or 1")
        norms = self.z_measurement_norms(label)
        probability = Fraction(norms[outcome], sum(norms))
        return (self._select_z(label, outcome) if probability else None), probability
```

**Source: `src/sparse_wavefunction.py` — `SparseState.measure_z`**

```python
    def measure_z(self, label: str, rng: Random) -> tuple[SparseState, int, Fraction]:
        norms = self.z_measurement_norms(label)
        outcome = sample_binary(*norms, rng)
        return self._select_z(label, outcome), outcome, Fraction(norms[outcome], sum(norms))
```


For a Z measurement of the bit \(z\), calculate

\[
N_s=\sum_y w(s,y)^2,\qquad \Pr(s)=\frac{N_s}{N_0+N_1}=\frac{N_s}{N}.
\]

`measure_z` samples \(s\), retains weights \(w(s,y)\), and removes the measured coordinate. The resulting normalized state is \(\sum_y w(s,y)|y\rangle/\sqrt{N_s}\). `project_z` selects a specified outcome without random sampling, and returns `None` if that outcome is impossible.

## 4. Circuit setup in `simulate_c4_helix_sparse.py`

### `CircuitSpecification`, its properties and `validate`

**Source: `src/simulate_c4_helix_sparse.py` — `CircuitSpecification`**

```python
@dataclass(frozen=True)
class CircuitSpecification:
    """Physical geometry and source generators; defaults are the full V2 circuit.

    Source supports specify products of Xs whose uniform span is prepared
    by the actual H/CNOT source schedules. Smaller specifications allow an
    independent dense comparison without changing the simulation algorithm.
    """

    data_qubits: int = 20
    edges: tuple[tuple[int, int], ...] = EDGES
    controllers: tuple[int, ...] = CONTROLLERS
    tree_edges: tuple[int, ...] = TREE_EDGES
    b_source_generators: tuple[tuple[int, ...], ...] = CHECK_SUPPORTS
    c_source_generators: tuple[tuple[int, ...], ...] = CHECK_SUPPORTS + (LOGICAL_X0,)
    b_logical_z0: tuple[int, ...] = LOGICAL_Z0

    @property
    def vertex_count(self) -> int:
        return len(self.tree_edges) + 1

    @property
    def vertex_labels(self) -> tuple[str, ...]:
        return tuple(f"V_{chr(ord('a') + v)}" for v in range(self.vertex_count))

    def validate(self) -> None:
        if self.data_qubits < 1 or len(self.controllers) != self.data_qubits:
            raise ValueError("Each data pair needs exactly one controller")
        if not self.edges or self.vertex_count < 2:
            raise ValueError("A connected gauge graph with at least two vertices is required")
        if any(v < 0 or v >= self.vertex_count for v in self.controllers):
            raise ValueError("Controller vertex is outside the graph")
        for u, v in self.edges:
            if not (0 <= u < v < self.vertex_count):
                raise ValueError("Edges must have distinct, alphabetically ordered endpoints")
        for v, q in enumerate(self.tree_edges, 1):
            if q < 0 or q >= len(self.edges) or self.edges[q] != (0, v):
                raise ValueError("Tree edges must connect root a to the other vertices in order")
        for support in self.b_source_generators + self.c_source_generators + (self.b_logical_z0,):
            if len(set(support)) != len(support) or any(q < 0 or q >= self.data_qubits for q in support):
                raise ValueError("Invalid physical source/readout support")
```


This dataclass defines the number of data qubits, graph edges, the vertex controlling each B/C pair, the root tree edges, source generators, and the support of logical \(Z_0\). `vertex_count` is one plus the number of tree edges; `vertex_labels` gives the corresponding names. `validate` checks indices, unique supports and the required root-to-vertex tree-edge layout. These checks do not evolve a state or perform measurements.

### `prepare_source` and `preparation_schedule`

**Source: `src/simulate_c4_helix_sparse.py` — `prepare_source`**

```python
def prepare_source(supports: tuple[tuple[int, ...], ...],
                   labels: tuple[str, ...]) -> SparseState:
    """Integrated V2 Section 5: prepare known inputs without checking syndromes.

    |00_L> = 2^(-9/2) sum_{u in {0,1}^9} prod_s (S_s^X)^u_s |0^20>,
    |+0_L> = (I + Xbar_0)|00_L>/sqrt(2).

    We execute preparation_schedule's H and CNOT gates; we do not initialize
    a precomputed set of valid codewords or measure any source stabilizer.
    """
    hadamards, cnots = preparation_schedule(supports, len(labels))
    state = SparseState.zeros(labels)
    for q in hadamards:
        state = state.hadamard(labels[q])
    for control, target in cnots:
        state = state.cnot(labels[control], labels[target])
    return state
```

**Source: `src/c4_helix_noiseless.py` — `preparation_schedule`**

```python
def preparation_schedule(supports, n_qubits=20):
    """Return the H-qubit list and CNOT pairs that prepare the encoded inputs.

    Each support R_s represents S_s^X = product_{q in R_s} X_q. For B:

        |00_L> = (1/sqrt(2^9)) sum_{u in {0,1}^9}
                     (S_0^X)^u_0 ... (S_8^X)^u_8 |0>^20.

    Each binary choice u_s includes or omits one X stabilizer. The sum has
    512 distinct physical bit strings, all with the same positive amplitude.
    For C, append the support of logical X_0, giving one more binary choice:

        |+0_L> = (|00_L> + |10_L>)/sqrt(2)
               = (I + Xbar_0)|00_L>/sqrt(2)
               = (1/sqrt(2^10)) sum_{a in {0,1}, u in {0,1}^9}
                     Xbar_0^a (S_0^X)^u_0 ... (S_8^X)^u_8 |0>^20.

    To implement these sums, row reduction replaces the generators by an
    equivalent set with one exclusive pivot qubit per generator. H on each
    pivot supplies its binary choice; CNOTs copy it to that generator's other
    positions. The caller starts in physical zeros; no checks are measured.
    """
    # A row explicitly lists which qubits an X generator flips.
    # For example, support (0, 2) on three qubits becomes [1, 0, 1].
    generator_rows = [
        [1 if qubit in support else 0 for qubit in range(n_qubits)]
        for support in supports
    ]
    pivot_qubits = []

    for qubit in range(n_qubits):
        next_row = len(pivot_qubits)

        # Find an unused generator containing this qubit.
        selected_row = None
        for row_index in range(next_row, len(generator_rows)):
            if generator_rows[row_index][qubit] == 1:
                selected_row = row_index
                break
        if selected_row is None:
            continue

        generator_rows[next_row], generator_rows[selected_row] = (
            generator_rows[selected_row], generator_rows[next_row]
        )
        pivot_row = generator_rows[next_row]

        # Make this qubit exclusive to the chosen generator. Multiplying
        # X generators adds their rows modulo 2: two Xs on one qubit cancel.
        # This changes the generators but preserves the set of terms in the sum.
        for row_index, row in enumerate(generator_rows):
            if row_index != next_row and row[qubit] == 1:
                generator_rows[row_index] = [
                    (entry + pivot_entry) % 2
                    for entry, pivot_entry in zip(row, pivot_row)
                ]
        pivot_qubits.append(qubit)

    if len(pivot_qubits) != len(generator_rows):
        raise ValueError("Source generators must be independent")

    # After H, each pivot is a coherent choice of 0 or 1. Copy that choice
    # to the remaining positions of its generator using CNOTs.
    cnot_pairs = []
    for pivot, row in zip(pivot_qubits, generator_rows):
        for target, includes_qubit in enumerate(row):
            if target != pivot and includes_qubit == 1:
                cnot_pairs.append((pivot, target))

    return tuple(pivot_qubits), tuple(cnot_pairs)
```


For each support \(R_j\), define \(S_j^X=\prod_{q\in R_j}X_q\). The B and C sources are

\[
|B\rangle=|\overline{00}\rangle
=\frac{1}{\sqrt{2^9}}\sum_{u\in\{0,1\}^9}
\prod_{j=0}^{8}(S_j^X)^{u_j}|0^{20}\rangle,
\]
\[
|C\rangle=|\overline{+0}\rangle
=\frac{I+\overline X_0}{\sqrt2}|\overline{00}\rangle.
\]

The function calls `preparation_schedule` from [`c4_helix_noiseless.py`](../src/c4_helix_noiseless.py), starts from \(|0^{20}\rangle\), then applies its H gates and CNOTs. The schedule row-reduces the binary generator supports modulo 2. Each resulting row has a pivot absent from all other rows. H on each pivot creates a coherent binary choice, and CNOTs copy that choice into the row's other positions. Row operations preserve the generator span. The nine independent B generators give \(2^9=512\) strings; C includes the independent logical \(X_0\) generator and has \(2^{10}=1024\). There is no syndrome measurement here.

### `build_gauge_preimages`

**Source: `src/simulate_c4_helix_sparse.py` — `build_gauge_preimages`**

```python
def build_gauge_preimages(edges: tuple[tuple[int, int], ...],
                         vertex_count: int = 5) -> dict[str, tuple[str, str]]:
    """Section 6: |Gamma> = 2^(-5/2) sum_t |t>|p(t)>; p(t)_q=t_u+t_v.

    Follow the two graph CNOTs for each edge, on the 32 small vertex labels.
    Verify two complementary preimages per gauge word before early sampling.
    """
    table: dict[str, list[str]] = {}
    for vertex_bits in product((0, 1), repeat=vertex_count):
        gauge_bits = [0] * len(edges)
        for q, (u, v) in enumerate(edges):
            gauge_bits[q] = (gauge_bits[q] + vertex_bits[u]) % 2
            gauge_bits[q] = (gauge_bits[q] + vertex_bits[v]) % 2
        gauge_word = "".join(map(str, gauge_bits))
        table.setdefault(gauge_word, []).append("".join(map(str, vertex_bits)))
    if len(table) != 2 ** (vertex_count - 1):
        raise ValueError("The graph must be connected")
    for preimages in table.values():
        if len(preimages) != 2 or any(a == b for a, b in zip(*preimages)):
            raise ValueError("Every gauge outcome needs two complementary vertex strings")
    return {word: (values[0], values[1]) for word, values in table.items()}
```


Let \(t=(t_a,t_b,t_c,t_d,t_e)\in\{0,1\}^5\) be a vertex string. For an edge \(q=(u,v)\), the gauge bit is

\[
p(t)_q=t_u\oplus t_v.
\]

The function enumerates all 32 vertex strings, calculates \(p(t)\), and groups the strings by gauge word \(m\). The graph is connected, so \(p(t)=p(\bar t)\), and each word has exactly those two complementary preimages. It checks that there are 16 words and two complementary preimages for each. This table is a classical description of the graph state; creating it is not a measurement.

### `sample_gauge`

**Source: `src/simulate_c4_helix_sparse.py` — `sample_gauge`**

```python
def sample_gauge(table: dict[str, tuple[str, str]], rng: Random) -> tuple[str, tuple[str, str]]:
    """Pr(m)=2/32=1/16 for the checked graph. Keep both coherent preimages."""
    words = tuple(table)
    word = words[rng.randrange(len(words))]
    return word, table[word]
```


The prepared graph state is

\[
|\Gamma\rangle_{VA}=\frac{1}{\sqrt{32}}\sum_t |t\rangle_V|p(t)\rangle_A.
\]

The function samples one of the 16 gauge words uniformly, \(\Pr(m)=2/32=1/16\), and returns it **with both** preimages. For \(p(t)=m\), the conditional graph state is

\[
|\Gamma_m\rangle=\frac{|t\rangle_V+|\bar t\rangle_V}{\sqrt2}\otimes|m\rangle_A.
\]

The gauge measurement is moved earlier only in the noiseless simulation: its projector commutes with the intervening V/BC operations and the diagonal gauge feedforward. See Section 3 of the simulation plan for the proof and its limitations. The gadget circuit has extra noncommuting interactions, so this argument does not automatically apply there. If a shot is rejected at vertex selection, its early gauge sample is internal and is not reported as a physical readout.

### `SparseC4HelixSimulator.__init__` and `conditioned_input`

**Source: `src/simulate_c4_helix_sparse.py` — `SparseC4HelixSimulator.__init__`**

```python
    def __init__(self, specification: CircuitSpecification | None = None):
        self.specification = specification or CircuitSpecification()
        self.specification.validate()
        n = self.specification.data_qubits
        self.b_labels = tuple(f"B_{q}" for q in range(n))
        self.c_labels = tuple(f"C_{q}" for q in range(n))
        self.b_source = prepare_source(self.specification.b_source_generators, self.b_labels)
        self.c_source = prepare_source(self.specification.c_source_generators, self.c_labels)
        self.gauge_table = build_gauge_preimages(self.specification.edges,
                                                self.specification.vertex_count)
```

**Source: `src/simulate_c4_helix_sparse.py` — `SparseC4HelixSimulator.conditioned_input`**

```python
    def conditioned_input(self, preimages: tuple[str, str]) -> SparseState:
        """Construct (|t>+|t_bar>)/sqrt(2) tensor |psi>, with fixed m metadata.

        Construct the two vertex prefixes directly, avoiding a second large
        BC tensor-product dictionary. The weights keep both coherent terms.
        """
        weights = {}
        for vertices in preimages:
            for b_word, b_weight in self.b_source.weights.items():
                prefix = vertices + b_word
                for c_word, c_weight in self.c_source.weights.items():
                    weights[prefix + c_word] = b_weight * c_weight
        labels = self.specification.vertex_labels + self.b_labels + self.c_labels
        return SparseState(labels, weights)
```


The constructor validates the specification, creates labels, prepares the two source dictionaries, and builds the gauge table. Given the sampled pair \(t,\bar t\), `conditioned_input` creates

\[
\frac{|t\rangle+|\bar t\rangle}{\sqrt2}\otimes|B\rangle\otimes|C\rangle.
\]

For each vertex prefix and each source pair, it stores the product of the B and C integer weights. The fixed gauge word \(m\) is metadata, not 20 additional characters in every key. The full default initial conditional state has

\[
2\times512\times1024=1{,}048{,}576
\]

entries. Both vertex prefixes and every B/C component are retained.

### `enrich`

**Source: `src/simulate_c4_helix_sparse.py` — `SparseC4HelixSimulator.enrich`**

```python
    def enrich(self, state: SparseState) -> SparseState:
        """Section 7: sum_t |t>|p(t)> V_t|psi>/sqrt(32), conditioned on m.

        Execute all twenty Fredkins in physical-label order. Controllers
        come from CONTROLLERS, independently of the endpoints of edge q.
        """
        for q, v in enumerate(self.specification.controllers):
            state = state.fredkin(self.specification.vertex_labels[v],
                                 self.b_labels[q], self.c_labels[q])
        return state
```


For physical data index \(q\), let \(v(q)\) be its controlling vertex. The function applies one Fredkin controlled by \(V_{v(q)}\) to \(B_q,C_q\), for each of the 20 data pairs. Write \(V_t\) for the product of SWAPs enabled by vertex string \(t\), and \(|\psi\rangle=|B\rangle|C\rangle\). The state becomes

\[
\frac{|t\rangle V_t|\psi\rangle+|\bar t\rangle V_{\bar t}|\psi\rangle}{\sqrt2}.
\]

This is a coherent gate update, not a choice between the two terms.

### `apply_vertex_feedforward`

**Source: `src/simulate_c4_helix_sparse.py` — `SparseC4HelixSimulator.apply_vertex_feedforward`**

```python
    def apply_vertex_feedforward(self, state: SparseState, vertex_x: tuple[int, ...],
                                 gauge_word: str) -> SparseState:
        """Section 8.4: F_b=Z_A7^b_b Z_A11^b_c Z_A3^b_d Z_A0^b_e.

        For fixed gauge word m, F_b|m> = (-1)^theta |m>,
        theta=b_b*m7+b_c*m11+b_d*m3+b_e*m0 (mod 2).
        Apply this sign explicitly even though it is global on this trajectory.
        """
        exponent = sum(vertex_x[v] * int(gauge_word[q])
                       for v, q in enumerate(self.specification.tree_edges, 1))
        return state.global_sign((-1) ** (exponent % 2))
```


For measured vertex bits \(b=(b_a,b_b,b_c,b_d,b_e)\), the physical gauge operation is

\[
F_b=Z_{A_7}^{b_b}Z_{A_{11}}^{b_c}Z_{A_3}^{b_d}Z_{A_0}^{b_e}.
\]

The simulator has already fixed \(m\), so this becomes the global sign

\[
F_b|m\rangle=(-1)^\theta|m\rangle,\qquad
\theta=b_bm_7+b_cm_{11}+b_dm_3+b_em_0\pmod2.
\]

The code calculates \(\theta\) and calls `global_sign`. This sign has no effect on probabilities within the conditioned trajectory; recording it makes the feedforward action explicit.

### `correct_swaps`

**Source: `src/simulate_c4_helix_sparse.py` — `SparseC4HelixSimulator.correct_swaps`**

```python
    def correct_swaps(self, state: SparseState, gauge_word: str) -> tuple[SparseState, tuple[int, ...]]:
        """Sections 12--13: t_hat=(0,m7,m11,m3,m0); apply V_t_hat.

        V_t_hat[V_t Pi_+|psi>] = Pi_+|psi>, Pi_+=(I+U)/2.
        The corrected state's expected normalized form is
        (|psi>+U|psi>)/sqrt(3); it is never directly initialized here.
        """
        offsets = (0,) + tuple(int(gauge_word[q]) for q in self.specification.tree_edges)
        for q, v in enumerate(self.specification.controllers):
            if offsets[v]:
                state = state.swap(self.b_labels[q], self.c_labels[q])
        return state, offsets
```


The tree gauge bits give the relative vertex choices with the root fixed to zero:

\[
\hat t=(0,m_7,m_{11},m_3,m_0).
\]

For every data pair whose controller \(v(q)\) has \(\hat t_{v(q)}=1\), the function swaps \(B_q,C_q\). These swaps implement \(V_{\hat t}\), using the sampled gauge word. For a retained even vertex outcome, they turn the two contributions into the positive global-SWAP projection

\[
\Pi_+|\psi\rangle,\qquad \Pi_+=\frac{I+U}{2},
\]

up to normalization and an irrelevant global phase, where \(U\) swaps the full B and C registers. For these particular inputs the normalized state is \((|\psi\rangle+U|\psi\rangle)/\sqrt3\). The code obtains it by gate and measurement updates; it does not initialize that formula directly.

## 5. `simulate_attempt`: follow one shot

**Source: `src/simulate_c4_helix_sparse.py` — `SparseC4HelixSimulator.simulate_attempt`**

```python
    def simulate_attempt(self, rng: Random, shot_index: int = 0,
                         observer: StageObserver | None = None) -> ShotResult:
        """One exact trajectory; Pr(vertex b|m)=3/64 even, 1/64 odd in the full circuit.

        Vertex and B probabilities are calculated from the current amplitudes,
        not inserted from the expected logical-state formulas. The observer
        may inspect a stage but should not retain its large intermediate state.
        """
        started = perf_counter()
        result = ShotResult(shot_index)

        def observe(stage: str, state: SparseState) -> None:
            result.metrics.peak_state_entries = max(result.metrics.peak_state_entries, len(state.weights))
            if observer is not None:
                observer(stage, state)

        def finish() -> ShotResult:
            result.metrics.elapsed_seconds = perf_counter() - started
            result.metrics.process_peak_rss_bytes = process_peak_rss_bytes()
            return result

        # Reordered internal sample. It becomes a public measurement only if
        # the physical circuit reaches gauge readout after vertex selection.
        internal_m, preimages = sample_gauge(self.gauge_table, rng)
        state = self.conditioned_input(preimages)
        observe("conditioned_input", state)
        state = self.enrich(state)
        observe("enriched", state)

        vertex_bits = []
        for label in self.specification.vertex_labels:
            state, bit, probability = state.measure_x(label, rng)
            vertex_bits.append(bit)
            result.vertex_probability_given_gauge *= probability
            observe(f"measured_{label}_in_X", state)
        result.vertex_x = tuple(vertex_bits)
        result.swap_plus = sum(vertex_bits) % 2 == 0
        if not result.swap_plus:
            # No physical gauge/B record is produced on this rejection path.
            return finish()

        observe("before_vertex_feedforward", state)
        state = self.apply_vertex_feedforward(state, result.vertex_x, internal_m)
        observe("after_vertex_feedforward", state)
        result.gauge_z = internal_m
        state, result.swap_offsets = self.correct_swaps(state, internal_m)
        observe("after_swap_correction", state)

        # Section 16: h_s recovery is absent in the noiseless implementation.
        # Sample actual physical B reports, then evaluate the logical parity.
        b_bits = []
        result.b_probability_given_vertex_gauge = Fraction(1)
        for label in self.b_labels:
            state, bit, probability = state.measure_z(label, rng)
            b_bits.append(bit)
            result.b_probability_given_vertex_gauge *= probability
        result.b_z = "".join(map(str, b_bits))
        result.b_logical_z0 = sum(b_bits[q] for q in self.specification.b_logical_z0) % 2
        result.accepted = result.b_logical_z0 == 0
        if result.accepted:
            result.c_state = state
            observe("accepted_C", state)
        return finish()
```


This function ties the pieces together. Its `rng` supplies pseudorandom draws, while `shot_index` labels the record.

1. **Sample gauge.** `sample_gauge` picks \(m\); `conditioned_input` keeps its two coherent vertex preimages and all source amplitudes.
2. **Enrich.** `enrich` applies all Fredkins to the state.
3. **Measure vertices.** For each of the five vertices, `measure_x` calculates two norms, samples one bit, and retains the complete conditional wave function. For outcome \(b\), after all five measurements the BC vector is proportional to
   \[
   V_t|\psi\rangle+(-1)^{b_a+b_b+b_c+b_d+b_e}V_{\bar t}|\psi\rangle,
   \]
   up to an overall sign. Each conditional probability is multiplied into `vertex_probability_given_gauge`, so the stored product is \(\Pr(b\mid m)\). For the default input, the code documents the check values \(3/64\) for each even \(b\) and \(1/64\) for each odd \(b\); it calculates the probabilities from the state rather than inserting those values.
4. **Postselect vertices.** If \(\sum_v b_v\) is odd, stop and reject. No gauge or B readout is reported for that shot. If even, apply vertex feedforward, expose the sampled \(m\) as the gauge readout, and apply `correct_swaps`.
5. **Measure B.** For each physical B qubit, `measure_z` samples a bit using the current state, removes the measured coordinate, and retains the exact state conditioned on the bit. The product of these probabilities is `b_probability_given_vertex_gauge`.
6. **Postselect logical parity.** With B readout bits \(s_q\) and logical support \(L_Z\), calculate \(\ell=\sum_{q\in L_Z}s_q\pmod2\). Accept if \(\ell=0\). On acceptance, the remaining unmeasured state is `c_state`; on rejection it is not returned as an output state.

`observe` records the number of entries at the observed stages and can call an optional observer. `finish` records elapsed time and process peak memory. The `ShotResult` dataclass holds the record, conditional probabilities and, on acceptance, the C state. It does not contain wave functions for all unsampled outcomes.

### `iter_attempts`

**Source: `src/simulate_c4_helix_sparse.py` — `SparseC4HelixSimulator.iter_attempts`**

```python
    def iter_attempts(self, number_of_attempts: int, seed: int | None = None,
                      observer: StageObserver | None = None) -> Iterator[ShotResult]:
        """Yield one result at a time. Intermediate wavefunctions are not cached."""
        if number_of_attempts < 0:
            raise ValueError("Number of attempts must be nonnegative")
        rng = Random(seed)
        for index in range(number_of_attempts):
            yield self.simulate_attempt(rng, index, observer)
```


Creates a pseudorandom generator from the optional seed and calls `simulate_attempt` sequentially. The number requested is the number of **attempts**, including rejections. Reusing a seed reproduces the pseudorandom stream for the same implementation. Repeated attempts produce sampled records; frequencies estimated from a finite number of attempts have sampling uncertainty.

## 6. Output and diagnostic functions

### `expectation_pauli` and `output_diagnostics`

**Source: `src/sparse_wavefunction.py` — `SparseState.expectation_pauli`**

```python
    def expectation_pauli(self, x_support: Sequence[int] = (),
                          z_support: Sequence[int] = ()) -> Fraction:
        """Exact expectation of P = i^k X(s)Z(z), k=|s intersect z|.

        A position in both supports denotes physical Y. The numerator before
        i^k is sum_x (-1)^(z.x) w(x) w(x+s). Real states have zero expectation
        for any Pauli with an odd number of Ys. No physical measurement is added.
        """
        xs, zs = set(x_support), set(z_support)
        if any(q < 0 or q >= len(self.labels) for q in xs | zs):
            raise ValueError("Pauli support is outside the state")
        numerator = 0
        for key, weight in self.weights.items():
            changed = list(key)
            for q in xs:
                changed[q] = "1" if key[q] == "0" else "0"
            other = self.weights.get("".join(changed), 0)
            sign = (-1) ** (sum(int(key[q]) for q in zs) % 2)
            numerator += sign * weight * other
        phase_power = len(xs & zs) % 4
        if phase_power in (1, 3):
            if numerator != 0:
                raise ArithmeticError("A Hermitian odd-Y Pauli must have zero expectation on a real state")
            return Fraction(0)
        sign = 1 if phase_power == 0 else -1
        return Fraction(sign * numerator, self.norm_squared())
```

**Source: `src/simulate_c4_helix_sparse.py` — `output_diagnostics`**

```python
def output_diagnostics(state: SparseState) -> dict:
    """Exact code/logical checks of the retained C state; no added measurements.

    Section 16 predicts |M0_L>, |M>=(2|0>+|1>)/sqrt(5), hence
    <Xbar_0>=4/5, <Zbar_0>=3/5, <Ybar_0>=0, <Zbar_1>=1.
    """
    if state.labels != tuple(f"C_{q}" for q in range(20)):
        raise ValueError("Full C4-Helix diagnostics require the twenty C coordinates")
    checks = [state.expectation_pauli(x_support=s) for s in CHECK_SUPPORTS]
    checks += [state.expectation_pauli(z_support=s) for s in CHECK_SUPPORTS]
    # In this code the physical Xbar_0 and Zbar_0 supports overlap once;
    # i Xbar_0 Zbar_0 is exactly the corresponding Hermitian Pauli string.
    return {"entries": len(state.weights), "norm_squared": state.norm_squared(),
            "weight_counts": dict(Counter(state.weights.values())),
            "in_original_code_space": all(value == 1 for value in checks),
            "logical_X0": str(state.expectation_pauli(x_support=LOGICAL_X0)),
            "logical_Z0": str(state.expectation_pauli(z_support=LOGICAL_Z0)),
            "logical_Y0": str(state.expectation_pauli(LOGICAL_X0, LOGICAL_Z0)),
            "logical_Z1": str(state.expectation_pauli(z_support=LOGICAL_Z1))}
```


For X support \(s\) and Z support \(z\), the backend represents the Hermitian physical Pauli string as \(P=i^k X(s)Z(z)\), where \(k=|s\cap z|\). For real integer weights,

\[
\langle P\rangle=\frac{i^k}{N}\sum_x(-1)^{z\cdot x}w(x)w(x\oplus s).
\]

Here \(x\oplus s\) flips bits in the X support, and \(z\cdot x\) counts the selected Z bits modulo 2. With an odd number of Y factors, the expectation is zero for a real state. This is an exact classical calculation from the stored wave function, **not an additional measurement on C**.

`output_diagnostics` applies this calculation to the C-code checks and logical observables. The expected accepted logical state is

\[
|M\rangle=\frac{2|0\rangle+|1\rangle}{\sqrt5},\qquad
\langle X\rangle=\frac45,\quad\langle Z\rangle=\frac35,\quad\langle Y\rangle=0,
\]

with the second logical qubit in \(|0\rangle\), so \(\langle\overline Z_1\rangle=1\). The diagnostics check the obtained state; they do not prepare it.

### `canonical_payload`, `from_payload`, `to_scipy_column`, `to_numpy`

**Source: `src/sparse_wavefunction.py` — `SparseState.canonical_payload`**

```python
    def canonical_payload(self) -> dict:
        """JSON-ready exact state, removing an irrelevant common scale and sign."""
        divisor = 0
        for weight in self.weights.values():
            divisor = gcd(divisor, abs(weight))
        if self.weights[min(self.weights)] < 0:
            divisor = -divisor
        weights = {key: self.weights[key] // divisor for key in sorted(self.weights)}
        return {"labels": list(self.labels), "weights": weights,
                "norm_squared": sum(value * value for value in weights.values())}
```

**Source: `src/sparse_wavefunction.py` — `SparseState.from_payload`**

```python
    @classmethod
    def from_payload(cls, payload: Mapping) -> SparseState:
        state = cls(tuple(payload["labels"]), dict(payload["weights"]))
        state.validate()
        if state.norm_squared() != payload["norm_squared"]:
            raise ValueError("Stored normalization does not match the integer weights")
        return state
```

**Source: `src/sparse_wavefunction.py` — `SparseState.to_scipy_column`**

```python
    def to_scipy_column(self) -> sparse.csc_array:
        """Export normalized floating amplitudes; the first label is the MSB.

        CSC stores only nonzero entries and a two-element column pointer.
        It does not allocate 2**n amplitudes. Export supports at most 62 labels
        so basis indices and the shape fit SciPy's signed integer indexing.
        """
        if len(self.labels) > 62:
            raise ValueError("SciPy export supports at most 62 coordinates")
        indices = np.fromiter((int(key, 2) if key else 0 for key in self.weights), dtype=np.int64)
        amplitudes = np.fromiter(self.weights.values(), dtype=np.float64) / sqrt(self.norm_squared())
        columns = np.zeros(len(indices), dtype=np.int64)
        return sparse.coo_array((amplitudes.astype(np.complex128), (indices, columns)),
                                shape=(2 ** len(self.labels), 1)).tocsc()
```

**Source: `src/sparse_wavefunction.py` — `SparseState.to_numpy`**

```python
    def to_numpy(self, max_qubits: int = 20) -> np.ndarray:
        """Explicit dense export for small independent comparison tests only."""
        if len(self.labels) > max_qubits:
            raise ValueError("Dense export exceeds max_qubits")
        return self.to_scipy_column().toarray().ravel()
```


`canonical_payload` divides weights by their greatest common divisor, chooses an overall sign so the lexicographically first key is positive, and stores the new squared norm. This changes neither normalized state nor physical predictions. `from_payload` reconstructs the state and validates its stored norm.

`to_scipy_column` exports normalized amplitudes \(w(x)/\sqrt N\) to a sparse floating-point column, with the first label as the most significant bit. `to_numpy` converts that column into a dense floating-point array and guards against excessive qubit counts. These exports use floating point; the underlying integer weights and `Fraction` probabilities remain exact.

### `write_result`, `main`, `process_peak_rss_bytes`, `AttemptMetrics`

**Source: `src/simulate_c4_helix_sparse.py` — `write_result`**

```python
def write_result(result: ShotResult, output_directory: Path) -> dict:
    """Save exact C data if present and return a JSON-ready physical shot record.

    Identical states up to a common real scale/sign share one content-named
    file. No intermediate states are serialized. The caller writes the record
    immediately to its JSONL stream.
    """
    reference = None
    diagnostics = None
    if result.c_state is not None:
        payload = result.c_state.canonical_payload()
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = sha256(serialized.encode()).hexdigest()
        reference = f"states/{digest}.json"
        destination = output_directory / reference
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            destination.write_text(serialized + "\n")
        diagnostics = output_diagnostics(result.c_state)
    return {"shot_index": result.shot_index, "accepted": result.accepted,
            "vertex_x": result.vertex_x, "swap_plus": result.swap_plus,
            "gauge_z": result.gauge_z, "swap_offsets": result.swap_offsets,
            "b_z": result.b_z, "b_logical_z0": result.b_logical_z0,
            "vertex_probability_given_gauge": str(result.vertex_probability_given_gauge),
            "b_probability_given_vertex_gauge":
                (str(result.b_probability_given_vertex_gauge)
                 if result.b_probability_given_vertex_gauge is not None else None),
            "c_state_reference": reference, "c_diagnostics": diagnostics,
            "metrics": vars(result.metrics)}
```

**Source: `src/simulate_c4_helix_sparse.py` — `main`**

```python
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots", type=int, default=1, help="Number of attempts, including rejected attempts")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, default=Path("output/c4-helix-sparse"))
    parser.add_argument("--quiet", action="store_true", help="Suppress stage progress on stderr")
    args = parser.parse_args()
    if args.shots < 1:
        parser.error("--shots must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records_path = args.output_dir / "shots.jsonl"
    if records_path.exists():
        parser.error(f"{records_path} already exists; choose another --output-dir")

    def progress(stage: str, state: SparseState) -> None:
        if not args.quiet:
            print(f"{stage}: {len(state.weights):,} basis entries", file=sys.stderr, flush=True)

    simulator = SparseC4HelixSimulator()
    accepted = 0
    start = perf_counter()
    with records_path.open("x") as stream:
        for result in simulator.iter_attempts(args.shots, args.seed, progress):
            record = write_result(result, args.output_dir)
            stream.write(json.dumps(record) + "\n")
            stream.flush()
            accepted += result.accepted
            del record, result
    summary = {"attempts": args.shots, "accepted": accepted, "seed": args.seed,
               "elapsed_seconds": perf_counter() - start,
               "process_peak_rss_bytes": process_peak_rss_bytes(),
               "b_source_entries": len(simulator.b_source.weights),
               "c_source_entries": len(simulator.c_source.weights),
               "gauge_words": len(simulator.gauge_table), "ideal_success_probability": "5/8"}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"Shot records: {records_path}")
```

**Source: `src/simulate_c4_helix_sparse.py` — `process_peak_rss_bytes`**

```python
def process_peak_rss_bytes() -> int:
    """Process-lifetime peak RSS, including imports and cached sources, not a delta."""
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)
```

**Source: `src/simulate_c4_helix_sparse.py` — `AttemptMetrics`**

```python
@dataclass
class AttemptMetrics:
    elapsed_seconds: float = 0.0
    peak_state_entries: int = 0
    process_peak_rss_bytes: int = 0
```


`write_result` writes a canonical accepted C state to a content-hashed JSON file and returns a JSON-ready shot record with diagnostics. `main` parses the shot count, seed and output directory, executes attempts serially, writes one JSONL record per attempt, and writes a summary. It refuses to overwrite an existing shot-record file. The summary's `ideal_success_probability` is a documented expected value, not an estimate computed from the sampled shots.

`AttemptMetrics` holds elapsed time, the largest **observed individual state** entry count and process peak resident memory. `process_peak_rss_bytes` obtains the process-lifetime peak, including imports and cached data; it is not the memory attributable to a single shot. During an update, old and new dictionaries can coexist, so the number of entries simultaneously allocated can exceed the largest individual state size.

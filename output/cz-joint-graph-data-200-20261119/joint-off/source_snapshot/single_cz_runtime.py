"""Elementary noisy quantum backend for run_single_block_cz_controller.

Independent Born/noise RNGs; no sampled-fault cap or syndrome oracle.
Physical T/Tdg receive individual noise, and every live waiting qubit has
one idle per serial operation, plus explicit boundary idles.
"""
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from random import Random
from time import perf_counter
import c4_helix_single_block_cz as m
from single_cz_state import CoherentState


def probability(value):
    if isinstance(value,bool):
        raise ValueError("Boolean probability")
    try:
        p = Fraction(str(value))
    except (ValueError,TypeError,ZeroDivisionError,OverflowError) as exc:
        raise ValueError("Expected finite rational probability") from exc
    if not 0 <= p <= 1:
        raise ValueError("Probability outside [0,1]")
    return p


def pauli_probability(r,n):
    p = probability(r)*Fraction(2**n+1,2**n)
    if p > 1:
        raise ValueError("Average infidelity exceeds depolarizing maximum")
    return p


def coin(rng,p):
    return bool(p == 1 or (p and rng.randrange(p.denominator) < p.numerator))


def pauli_word(rng,n):
    code = rng.randrange(1,4**n)
    return tuple("IXYZ"[(code >> (2*j)) & 3] for j in range(n))


@dataclass(frozen=True)
class NoiseModel:
    two_qubit_infidelity: object = "1e-3"
    one_qubit_infidelity: object = "0"
    t_infidelity: object = None
    idle_infidelity: object = "0"
    preparation_flip_probability: object = "0"
    readout_flip_probability: object = "1e-3"

    def __post_init__(self):
        for key in self.__dataclass_fields__:
            value = getattr(self,key)
            if key == "t_infidelity" and value is None:
                value = self.one_qubit_infidelity
            object.__setattr__(self,key,probability(value))
        for name,n in (("two_qubit_infidelity",2),("one_qubit_infidelity",1),
                       ("t_infidelity",1),("idle_infidelity",1)):
            pauli_probability(getattr(self,name),n)

    def manifest(self):
        return {"name":"independent_Pauli_depolarizing","gate_rate_convention":"average_gate_infidelity",
                "rates":{k:str(getattr(self,k)) for k in self.__dataclass_fields__},
                "nonidentity_probabilities":{"CX":str(pauli_probability(self.two_qubit_infidelity,2)),
                                              "Clifford_1q":str(pauli_probability(self.one_qubit_infidelity,1)),
                                              "T_TDG":str(pauli_probability(self.t_infidelity,1)),
                                              "idle":str(pauli_probability(self.idle_infidelity,1))},
                "controlled_W":"T^s,CX,T^-s; individual physical locations",
                "quantum_timing":"gate noise after ideal gate; idle noise before operation",
                "readout":"independent classical report flip after actual quantum measurement",
                "preparation":"X after |0> preparation","fault_count_cap":None,
                "idles":"one per live nonparticipant per serial operation, and every live qubit at boundary",
                "duration_calibrated":False,"atomic_multiqubit_gates":[]}


class QuantumBackend:
    def __init__(self,seed=0,noise_seed=0,model=None,trace=None,max_terms=4096,
                 max_factors=4096,max_operations=200000,injections=(),data_labels=None,progress=None):
        self.data_labels = tuple(data_labels if data_labels is not None else (f"D{q}" for q in range(20)))
        self.state = CoherentState(self.data_labels,max_terms,max_factors)
        self.rng,self.noise_rng = Random(seed),Random(noise_seed)
        self.model = model if model is not None else NoiseModel()
        self.live = set()
        self.context = "initial"
        self.events,self.peak_live = 0,0
        self.gate_counts,self.opportunities,self.noise_counts = Counter(),Counter(),Counter()
        self.noise_events,self.injected_events,self.measurements = [],[],[]
        self.trace,self.progress = trace,progress
        self.max_operations = max_operations
        self.injections,self.injection_hits = list(injections),Counter()
        self.started = perf_counter()

    def _inject(self,timing,operation,targets):
        for j,fault in enumerate(self.injections):
            if fault.get("timing","after") != timing:
                continue
            if "event" in fault and fault["event"] != self.events:
                continue
            if "context" in fault and fault["context"] != self.context:
                continue
            if "operation" in fault and fault["operation"] != operation:
                continue
            if "targets" in fault and tuple(fault["targets"]) != tuple(targets):
                continue
            hit = self.injection_hits[j]
            self.injection_hits[j] += 1
            if hit != fault.get("occurrence",0):
                continue
            paulis = fault.get("paulis",{})
            allowed = self.live-set(targets) if timing == "idle" else set(targets)
            if not set(paulis) <= allowed or (timing == "idle" and len(paulis)>1):
                raise ValueError("Injected fault exceeds location participants")
            for q,p in paulis.items():
                if p not in "IXYZ":
                    raise ValueError("Invalid injected Pauli")
                if p != "I":
                    self.state.gate(p,q)
            event = {"injection":j,"event":self.events,"context":self.context,"operation":operation,
                     "timing":timing,"targets":list(targets),"paulis":paulis,
                     "flip_report":bool(fault.get("flip_report",False))}
            self.injected_events.append(event)
            if self.trace:
                self.trace({"kind":"injected_fault",**event})

    def _noise(self,channel,targets,p):
        self.opportunities[channel] += 1
        if coin(self.noise_rng,p):
            axes = ("X",) if channel == "preparation" else () if channel == "readout" else pauli_word(self.noise_rng,len(targets))
            for q,axis in zip(targets,axes):
                if axis != "I":
                    self.state.gate(axis,q)
            event = {"id":len(self.noise_events),"event":self.events,"context":self.context,
                     "channel":channel,"targets":list(targets),"axes":list(axes),
                     "flip_report":channel == "readout"}
            self.noise_events.append(event)
            self.noise_counts[channel] += 1
            if self.trace:
                self.trace({"kind":"noise",**event})
            return True
        return False

    def _start(self,operation,targets):
        if self.events >= self.max_operations:
            raise MemoryError("Bounded physical-operation limit exceeded")
        waiting = sorted(self.live-set(targets))
        self.gate_counts["IDLE"] += len(waiting)
        self._inject("idle",operation,targets)
        p = pauli_probability(self.model.idle_infidelity,1)
        if p:
            for q in waiting:
                self._noise("idle",(q,),p)
        else:
            self.opportunities["idle"] += len(waiting)
        self._inject("before",operation,targets)

    def _end(self,operation,targets,**details):
        self.gate_counts[operation] += 1
        self.peak_live = max(self.peak_live,len(self.live))
        event = {"kind":"physical","event":self.events,"context":self.context,"operation":operation,
                 "targets":list(targets),"live_qubits":len(self.live),"coherent_terms":len(self.state.terms),**details}
        if self.trace:
            self.trace(event)
        self.events += 1
        if self.progress and self.events % 500 == 0:
            self.progress(self)

    def prepare(self,label):
        if label in self.live:
            raise ValueError("Preparing a live qubit")
        self._start("PREP",(label,))
        if label not in self.state.labels():
            if label in self.data_labels:
                if any(q in self.live for q in self.data_labels):
                    raise ValueError("Partial known-data reinitialization is not supported")
                fid,s = self.state.store.intern(self.data_labels,[0],[0])
                self.state.combine((w,fid,c*s) for (w,f),c in self.state.terms.items())
            else:
                self.state.allocate(label)
        self.live.add(label)
        self._noise("preparation",(label,),self.model.preparation_flip_probability)
        self._inject("after","PREP",(label,))
        self._end("PREP",(label,))

    def gate(self,name,*targets):
        if len(set(targets)) != len(targets) or not set(targets) <= self.live:
            raise ValueError("Invalid gate participants")
        if name not in ("H","S","SDG","X","Y","Z","T","TDG","CX"):
            raise ValueError(name)
        if len(targets) != (2 if name == "CX" else 1):
            raise ValueError("Wrong gate arity")
        self._start(name,targets)
        self.state.gate(name,*targets)
        channel = "two_qubit" if name == "CX" else "T" if name in ("T","TDG") else "one_qubit"
        rate = {"two_qubit":self.model.two_qubit_infidelity,"T":self.model.t_infidelity,
                "one_qubit":self.model.one_qubit_infidelity}[channel]
        self._noise(channel,targets,pauli_probability(rate,len(targets)))
        self._inject("after",name,targets)
        self._end(name,targets)

    def measure_z(self,label):
        if label not in self.live:
            raise ValueError("Measuring absent qubit")
        self._start("MZ",(label,))
        actual,probabilities = self.state.measure_z(label,self.rng)
        self.live.remove(label)
        flip = self._noise("readout",(label,),self.model.readout_flip_probability)
        before = len(self.injected_events)
        self._inject("report","MZ",(label,))
        flip ^= sum(e["flip_report"] for e in self.injected_events[before:]) % 2
        reported = actual ^ int(flip)
        self.measurements.append({"event":self.events,"context":self.context,"label":label,
                                  "actual":actual,"reported":reported,
                                  "probability_one":probabilities["probability_one"]})
        self._end("MZ",(label,),actual=actual,reported=reported,**probabilities)
        return reported

    def boundary(self):
        self._start("BOUNDARY",())
        self._end("BOUNDARY",())

    def compress_data(self):
        self.state.compress_css()

    def absorb_parity_helper(self,label):
        self.state.absorb_basis_label(label)  # exact tensor regrouping, no physical operation

    def metrics(self):
        return {"physical_operations_and_boundaries":self.events,"gate_counts":dict(self.gate_counts),
                "peak_live_qubits":self.peak_live,"peak_coherent_terms":self.state.peak_terms,
                "peak_cached_factors":self.state.store.peak_factors,"factor_collections":self.state.store.collections,
                "exact_CSS_basis_compressions":self.state.css_compressions,
                "elapsed_seconds":perf_counter()-self.started,"channel_opportunities":dict(self.opportunities),
                "noise_event_counts":dict(self.noise_counts),"sampled_noise_events":len(self.noise_events),
                "injected_fault_events":len(self.injected_events)}

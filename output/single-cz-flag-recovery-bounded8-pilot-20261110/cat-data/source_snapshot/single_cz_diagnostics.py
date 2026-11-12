"""Read-only complex CSS recovery diagnostics for two-logical-qubit CZ magic.

No true circuit syndromes or fault list are read. Every ideal syndrome sector
is decoded using the fixed physical-radius-two table, then fixed GF2 fallback.
The physical controller never receives this diagnostic state information.
"""
from functools import lru_cache
import numpy as np
import c4_helix_single_block_cz as m
from single_cz_recovery import H,syndrome_component,physical_table,pure_error

X0,X1,Z0,Z1 = map(m.mask,(m.X0,m.X1,m.Z0,m.Z1))


@lru_cache(maxsize=512)
def solve(s):
    return pure_error([(0,h) for h in H],[(s >> j)&1 for j in range(9)],20)[0]


@lru_cache(maxsize=1)
def coordinates():
    out = {0:0}
    for j,h in enumerate(H):
        out.update({w ^ h:u | (1 << j) for w,u in tuple(out.items())})
    return out


def diagnose(indices,values,tolerance=1e-10):
    indices,values = np.asarray(indices),np.asarray(values,dtype=np.complex128)
    if len(indices) != len(values) or len(set(map(int,indices))) != len(indices):
        raise ValueError("Invalid sparse output")
    norm = float(np.vdot(values,values).real)
    if not np.isfinite(norm) or norm <= 0:
        raise ValueError("Invalid wavefunction norm")
    logical_x = (0,X0,X1,X0 ^ X1)
    groups,amplitudes = {},dict(zip(map(int,indices),values))
    coord = coordinates()
    for w,a in amplitudes.items():
        s = syndrome_component(w)
        c = w ^ solve(s)
        l = ((c & Z0).bit_count()%2) | (((c & Z1).bit_count()%2) << 1)
        h = c ^ logical_x[l]
        if h not in coord:
            raise ArithmeticError("Invalid CSS coordinate decomposition")
        groups.setdefault(s,np.zeros((4,512),dtype=np.complex128))[l,coord[h]] += a
    rho = np.zeros((4,4),dtype=np.complex128)
    small_weight = total = 0.0
    active = 0
    table = physical_table()
    for zs,vec in groups.items():
        step = 1
        while step < 512:
            view = vec.reshape(4,-1,2*step)
            a,b = view[:,:,:step].copy(),view[:,:,step:].copy()
            view[:,:,:step],view[:,:,step:] = a+b,a-b
            step *= 2
        for xs in range(512):
            amps = vec[:,xs]
            weight = float(np.vdot(amps,amps).real)
            if weight == 0:
                continue
            active += 1
            s = zs | (xs << 9)
            if s in table:
                rx,rz = table[s]
                small_weight += weight
            else:
                rx,rz = solve(zs),solve(xs)
            delta = solve(zs) ^ rx
            flip = ((delta & Z0).bit_count()%2) | (((delta & Z1).bit_count()%2) << 1)
            corrected = np.zeros(4,dtype=np.complex128)
            for l,a in enumerate(amps):
                corrected[l ^ flip] = (-1)**((rz & (solve(zs) ^ logical_x[l])).bit_count()%2)*a
            rho += np.outer(corrected,corrected.conj())
            total += weight
    expected = 512*norm
    if not abs(total-expected) <= tolerance*expected:
        raise ArithmeticError("Syndrome probability sum failed")
    rho /= total
    target = np.array([1,1,1,0],dtype=np.complex128)/np.sqrt(3)
    fidelity = float(np.vdot(target,rho @ target).real)
    if not -tolerance <= fidelity <= 1+tolerance:
        raise ArithmeticError("Invalid decoded fidelity")
    raw_overlap = sum(amplitudes.get(h,0)+amplitudes.get(h ^ X0,0)+amplitudes.get(h ^ X1,0) for h in coord)
    return {"diagnostic_only":True,"decoder":"ideal syndrome projection; fixed weight<=2 table, then GF2 fallback",
            "syndrome_convention":"Z bits 0..8; X bits 9..17",
            "decoded_target_fidelity":min(1.0,max(0.0,fidelity)),
            "decoded_target_infidelity":max(0.0,1.0-fidelity),
            "decoded_target_within_tolerance":abs(1-fidelity) <= tolerance,
            "raw_physical_target_fidelity":min(1.0,max(0.0,float(abs(raw_overlap)**2/(1536*norm)))),
            "probability_in_weight_two_lookup":min(1.0,max(0.0,small_weight/total)),
            "active_syndrome_sectors":active,"syndrome_probability_sum":total/expected,
            "logical_density_real":rho.real.tolist(),"logical_density_imag":rho.imag.tolist(),
            "numerical_diagnostic_tolerance":tolerance,"trajectory_arithmetic":"exact Z[zeta8] before output conversion"}

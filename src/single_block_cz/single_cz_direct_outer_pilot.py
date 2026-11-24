"""Report-driven experimental compact13 controllers on the existing backend."""

import c4_helix_single_block_cz as m
from run_single_block_cz_controller import Reject
from single_cz_controller import DataCheckFlag, SimulationController
from single_cz_direct_outer_ports import dressed_x_program
from single_cz_flag_recovery import decision as data_flag_decision
from single_cz_graph_stars import chord_correction
from single_cz_hybrid_study import bare_nonroot_gauss_program
from single_cz_joint_recovery import decision as joint_decision
from single_cz_recovery import COMPACT13, data_table

# The original 6th-index check is the XOR of the replacement, check 5 and inner check 2.
OUTER_SUPPORTS = (m.SUPPORTS[5], (0, 3, 4, 6, 12, 14, 16, 19), *m.SUPPORTS[7:])


class DressedFlag(Exception):
    def __init__(self, check, flags, parity):
        self.check, self.flags, self.parity = check, flags, parity


class DirectPilot(SimulationController):
    """Gauged votes then destructive cut decoding and the existing terminal screen."""

    def __init__(self, backend, *, thin=False, first_vote=False, outer_lookup=None, **options):
        super().__init__(backend, graph=COMPACT13, graph_stars="bare", terminal_policy="screen", **options)
        self.thin = thin
        self.first_vote = first_vote
        self.outer_lookup = outer_lookup
        self.direct_recoveries = 0
        self.successful_direct_recoveries = 0

    def coordinates(self):
        raise AssertionError("The direct pilot cannot use a global coordinate pass")

    def direct_meter(self, name, program):
        self.context(name)
        reports = {}
        for op, roles in program:
            if op == "PREP":
                self.prep(*roles)
            elif op == "MZ":
                reports[roles[0]] = self.mz(*roles)
            else:
                self.gate(op, *roles)
        parity = reports.pop("s")
        flags = sum(bit << int(flag[1:]) for flag, bit in reports.items())
        self.record.append({"check": name, "flags": reports, "reported_parity": parity})
        if flags:
            raise DressedFlag(name, flags, parity)
        return parity

    def dressed_x(self, prefix, check, support):
        return self.direct_meter(f"{prefix}/dressed_X/{check}", dressed_x_program(support, self.graph_choice))

    def bare_check(self, prefix, axis, check):
        return self.check(f"{prefix}/{axis}/{check}", [(axis, f"D{q}") for q in m.SUPPORTS[check]])

    def direct_stars(self, prefix):
        return [self.direct_meter(f"{prefix}/G/{v}", bare_nonroot_gauss_program(self.graph_choice, v))
                for v in range(1, 5)]

    def direct_code_record(self, prefix, z=None, *, short=False):
        if z is None:
            z = [self.bare_check(prefix, "Z", j) for j in range(9)]
        if short:
            return z + [self.bare_check(prefix, "X", j) for j in range(5)]
        inner = [self.bare_check(prefix, "X", j) if not any(z) and "/vote/" in prefix
                 else self.dressed_x(prefix, j, m.SUPPORTS[j]) for j in range(5)]
        outer = [self.dressed_x(prefix, j, support) for j, support in enumerate(OUTER_SUPPORTS, 5)]
        outer[1] ^= outer[0] ^ inner[2]
        if hasattr(self.b, "compress_data"):
            self.b.compress_data()
        return z + inner + outer

    def direct_reference(self, prefix, flagged):
        records = []
        for j in range(4 if flagged else self.history_limit):
            name = f"{prefix}/{j}"
            try:
                row = self.direct_code_record(name) + self.cycle_reports(name + "/cycle") + self.direct_stars(name)
            except (DataCheckFlag, DressedFlag) as flag:
                raise Reject("direct_diagnostic_flag") from flag
            records.append(row)
            if (flagged and len(records) >= 2 and records[-1] == records[-2]) or (
                    not flagged and self.reference(records) is not None):
                selected = records[-1] if flagged else records[self.reference(records)["selected"]]
                self.record.append({"direct_reference": prefix, "records": records, "selected": selected})
                return selected
        raise Reject("unstable_direct_reference")

    def gauged_pauli(self, x, z):
        """Apply V X^x Z^z V, ignoring the scalar phase of known feedback."""
        graph = self.graph_choice
        z_edges = z >> 20
        for q in range(20):
            if z >> q & 1:
                self.gate("Z", f"D{q}")
                if q >= 4:
                    z_edges ^= 1 << graph.tree[q // 4 - 1]
        for e in range(len(graph.edges)):
            if z_edges >> e & 1:
                self.gate("Z", f"A{e}")
        for q in range(20):
            if not x >> q & 1:
                continue
            data = f"D{q}"
            if q >= 4:
                edge = f"A{graph.tree[q // 4 - 1]}"
                self.gate("SDG" if m.SIGNS[q] == 1 else "S", edge)
                self.gate("H", data)
                self.gate("CX", edge, data)
                self.gate("H", data)
            self.gate("X", data)
        for e in range(len(graph.edges)):
            if x >> (20 + e) & 1:
                self.gate("X", f"A{e}")
                if e in graph.tree:
                    self.apply_block_w(graph.tree.index(e) + 1)

    def apply_block_w(self, v):
        for q in range(4 * v, 4 * v + 4):
            self.gate("S" if m.SIGNS[q] == 1 else "SDG", f"D{q}")
            self.gate("X", f"D{q}")

    def direct_recover(self, prefix, flag=None):
        self.direct_recoveries += 1
        if isinstance(flag, DressedFlag) and self.outer_lookup is None:
            raise Reject("direct_outer_flag:" + flag.check)
        selected = self.direct_reference(prefix, flag is not None)
        graph = self.graph_choice
        cycles_end = 18 + len(graph.cycles)
        syndrome = sum(bit << j for j, bit in enumerate(selected[:18]))
        if isinstance(flag, DressedFlag):
            correction = self.outer_lookup(flag, selected)
        else:
            if flag is not None:
                record = flag.record
                locate = (record["axes"][0], tuple(int(q[1:]) for q in record["targets"]))
                flags = sum(b << j for j, b in enumerate(record["flags"]))
                row = data_flag_decision(*locate, flags, selected[:18], record["extraction"])
            else:
                row = data_table().get(syndrome, {})
                if row.get("correction") is None:
                    row = joint_decision(graph, selected[:cycles_end])
            correction = row.get("correction")
            if correction is not None:
                x, z = correction
                x |= m.mask(20 + e for e in chord_correction(graph, selected[18:cycles_end]))
                z |= m.mask(20 + e for e, bit in zip(graph.tree, selected[cycles_end:]) if bit)
                correction = x, z
        self.record.append({"direct_recovery": prefix, "correction": correction})
        if correction is None:
            raise Reject("direct_recovery_no_unique_class")
        self.context(prefix + "/correction")
        self.gauged_pauli(*correction)
        self.successful_direct_recoveries += 1
        self.data_epoch += 1

    def gauging(self):
        self.graph()
        graph = self.graph_choice
        self.context("enrichment")
        for q in range(20):
            self.cw(f"a{q // 4}", q)
        self.context("vertex_readout")
        bits = []
        for v in range(5):
            vertex = f"a{v}"
            self.gate("H", vertex)
            bits.append(self.mz(vertex))
        passed = int(self.first_vote and sum(bits) % 2 == 0)
        self.record.append({"vertex_reports": bits, "entry_vote": self.first_vote, "passes": passed})
        self.context("vertex_frame")
        for bit, e in zip(bits[1:], graph.tree):
            if bit:
                self.gate("Z", f"A{e}")
        self.b.boundary()

        for r in range(5 - self.first_vote):
            name = f"direct/vote/{r}"
            try:
                z = [self.bare_check(name, "Z", j) for j in range(9)]
                reports = z if any(z) else self.direct_code_record(name, z, short=self.thin)
            except (DataCheckFlag, DressedFlag) as flag:
                self.direct_recover(name + "/flag_recovery", flag)
            else:
                parity_frame = 0
                if self.thin and not any(z):
                    # XOR of the five inner X outcomes is total data Z parity.
                    # A nonzero parity reverses the signed U vote.
                    parity_frame = sum(reports[9:]) % 2
                elif any(reports):
                    self.direct_recover(name + "/syndrome_recovery")
                stars = self.direct_stars(name)
                # Condition the root sign on the other Gauss reports in software.
                root = self.check(name + "/root_Gauss", [("W", f"D{q}") for q in range(4)] +
                                  [("X", f"A{e}") for e, uv in enumerate(graph.edges) if 0 in uv])
                passed += (root + sum(stars) + parity_frame) % 2 == 0
                self.record.append({"direct_vote": r, "root": root, "nonroot": stars,
                                    "inner_x_parity_frame": parity_frame, "passes": passed})
            self.b.boundary()
            if passed == 3:
                break
        if passed != 3:
            raise Reject("insufficient_direct_votes")

        self.flatten_final_cycles()
        self.context("edge_readout")
        word = sum(self.mz(f"A{e}") << e for e in range(len(graph.edges)))
        decoded = graph.decode(word, graph.radius)
        self.record.append({"edge_reports": word, "decoded": decoded})
        if decoded is None:
            raise Reject("direct_edge_cut_outside_radius")
        self.context("byproduct")
        for v in range(1, 5):
            if decoded["eta"] >> v & 1:
                self.apply_block_w(v)
        self.b.boundary()

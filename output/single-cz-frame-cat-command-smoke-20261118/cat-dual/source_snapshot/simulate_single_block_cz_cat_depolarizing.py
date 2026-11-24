"""Actual twenty-qubit-cat CZ baseline with the shared physical simulator.

Same source, code checks, recovery, noise channels and diagnostics as the
gauging runner. Only the CZ measurement uses a repaired GHZ20 resource,
twenty physical T/CX/Tdg ports and X readout of all twenty leaves.
No graph is allocated. No stochastic benchmark is run on import.
"""
from run_single_block_cz_controller import Controller
from single_cz_controller import SimulationController


class CatStateController(SimulationController):
    """Use the genuine cat measurement while retaining matched Pauli checks."""
    def __init__(self,backend,route="direct_cat",**kwargs):
        if route!="direct_cat":
            raise ValueError("Cat-state baseline has no gauging route")
        super().__init__(backend,route=route,**kwargs)

    def check(self,name,ports):
        if name.endswith("/U"):
            ports=tuple(ports)
            if ports!=tuple(("W",f"D{q}") for q in range(20)):
                raise ValueError("CZ cat must measure all twenty canonical W ports")
            # Bypass the ordinary flagged-check dispatch only for logical CZ.
            # self.cat is the existing physical, history-certified cat repair.
            bit=Controller.check(self,name,ports)
            self.record[-1].update(extraction="verified_cat_CZ",
                                   axes=[a for a,q in ports],targets=[q for a,q in ports])
            return bit
        return super().check(name,ports)


def simulate(**kwargs):
    """Programmatic entry point with the same arguments as the gauging runner."""
    from simulate_single_block_cz_depolarizing import simulate as shared_simulate
    route=kwargs.pop("route","direct_cat")
    extraction=kwargs.pop("direct_cz_extraction","cat")
    if route!="direct_cat" or extraction!="cat":
        raise ValueError("This entry point always uses the twenty-qubit-cat CZ measurement")
    return shared_simulate(route=route,direct_cz_extraction="cat",**kwargs)


def clean_costs(source_extraction=None,verification_extraction=None,flag_recovery="reject",data_checks="rolling_flags"):
    from simulate_single_block_cz_depolarizing import clean_costs as shared_costs
    return shared_costs(source_extraction,verification_extraction,direct_cz_extraction="cat",flag_recovery=flag_recovery,data_checks=data_checks)


if __name__=="__main__":
    from simulate_single_block_cz_depolarizing import main
    main(cat_baseline=True)

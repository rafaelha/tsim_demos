"""The d=5 cultivation circuits of Chan et al. (arXiv:2609.17706), as T-state circuits."""

import pathlib
import re

import stim
import tsim
from tsim.experimental import LogicalError

CIRCUITS = pathlib.Path(__file__).parents[2] / "circuits" / "chan_cultivation"

_T_FOR_S = {"S": "T", "S_DAG": "T_DAG"}


def load_s_proxy(name: str) -> stim.Circuit:
    """Return the S-state proxy ``name`` as a Stim circuit."""
    return stim.Circuit.from_file(CIRCUITS / name)


def load_t_circuit(name: str) -> tsim.Circuit:
    """Return ``name`` with every S and S_DAG swapped for T and T_DAG, as Chan et al. do."""
    text = (CIRCUITS / name).read_text()
    text = re.sub(r"(?m)^(\s*)(S_DAG|S)(?=\s|$)", lambda m: m[1] + _T_FOR_S[m[2]], text)
    return tsim.Circuit(text)


def show_errors(errors: list[LogicalError], count: int = 3) -> None:
    """Print the most likely ``count`` logical errors: each fault's flipped detectors."""
    for error in errors[:count]:
        faults = "  +  ".join(
            " ".join(str(term.dem_target) for term in fault.dem_error_terms) or "(nothing)"
            for fault in error.faults
        )
        print(
            f"{faults}\n"
            f"    P(undetected) = {error.undetected_probability:.3f},"
            f" P(logical flip) = {error.logical_flip_probability:.3f}"
        )

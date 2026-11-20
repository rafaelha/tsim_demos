"""Printing the logical errors of the d=5 cultivation circuits of Chan et al. (arXiv:2609.17706)."""

from tsim.experimental import LogicalError


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

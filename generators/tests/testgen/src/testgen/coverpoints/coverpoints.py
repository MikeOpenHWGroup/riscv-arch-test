# testgen/coverpoints/coverpoints.py
"""Coverpoint generator registry with automatic discovery."""

from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from random import seed

from testgen.data.test_data import TestData
from testgen.utils.common import myhash

# Type alias for coverpoint generator functions
CoverpointGenerator = Callable[[str, str, str, TestData], list[str]]

# Registry storage: list of (pattern, generator) tuples sorted by pattern length (longest first)
_COVERPOINT_GENERATORS: list[tuple[str, CoverpointGenerator]] = []


def add_coverpoint_generator(*patterns: str) -> Callable[[CoverpointGenerator], CoverpointGenerator]:
    """
    Decorator to register a generator for one or more coverpoint patterns.

    Args:
        patterns: One or more coverpoint prefixes this generator can process

    Example:
        @add_coverpoint_generator("cp_rd")
        def make_rd(instr_name, instr_type, coverpoint, test_data):
            ...
    """

    def decorator(func: CoverpointGenerator) -> CoverpointGenerator:
        for pattern in patterns:
            # Insert in sorted position (longest patterns first)
            # This ensures the most specific generator is matched
            pattern_len = len(pattern)
            insert_pos = 0
            for i, (existing_pattern, _) in enumerate(_COVERPOINT_GENERATORS):
                if pattern_len > len(existing_pattern):
                    insert_pos = i
                    break
                insert_pos = i + 1
            _COVERPOINT_GENERATORS.insert(insert_pos, (pattern, func))
        return func

    return decorator


def _discover_and_import_coverpoint_generators() -> None:
    """Auto-import all generator modules to trigger decorator registration."""
    package_dir = Path(__file__).parent

    # Recursively import all Python files except coverpoints.py and files starting with _
    for module_file in package_dir.rglob("*.py"):
        if module_file.stem != "coverpoints" and not module_file.stem.startswith("_"):
            # Convert file path to module path (e.g., special/branch.py -> testgen.coverpoints.special.branch)
            relative_path = module_file.relative_to(package_dir)
            module_parts = [*list(relative_path.parts[:-1]), relative_path.stem]
            module_name = "testgen.coverpoints." + ".".join(module_parts)
            import_module(module_name)


# Discover and import coverpoint generators at module load
_discover_and_import_coverpoint_generators()


# Coverpoints that don't need dedicated test generation
SKIP_COVERPOINTS = frozenset(
    {
        "cp_gpr_hazard_rw",
        "cp_gpr_hazard_w",
        "cp_gpr_hazard_r",
        "cp_imm_edges_6bit_n0",  # Used only for cross products
        "cp_rd_sign",  # Already covered by rd_edges
        "cmp_rd_rs1_eqval",  # Already covered by cr_rs1_rs2_edges
        "cmp_rd_rs2_eqval",  # Already covered by cr_rs1_rs2_edges
    }
)


def _select_coverpoint_generator(coverpoint: str) -> CoverpointGenerator:
    """Select generator using longest-prefix matching."""
    for pattern, generator in _COVERPOINT_GENERATORS:
        if coverpoint.startswith(pattern):
            return generator
    raise ValueError(f"No coverpoint generator found for coverpoint: {coverpoint}")


def generate_tests_for_coverpoint(instr_name: str, instr_type: str, coverpoint: str, test_data: TestData) -> str:
    """Generate tests for a specific coverpoint."""
    if coverpoint in SKIP_COVERPOINTS:
        return ""

    generator = _select_coverpoint_generator(coverpoint)
    hashval = myhash(instr_name + coverpoint)
    seed(hashval)
    test_lines = [f"\n\n{coverpoint}_tests:"]
    test_lines.extend(generator(instr_name, instr_type, coverpoint, test_data))
    return "\n".join(test_lines)

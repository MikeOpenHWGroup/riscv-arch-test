# testgen/coverpoints/cp_memval.py
"""cp_memval coverpoint generator."""

from testgen.coverpoints.coverpoints import add_coverpoint_generator
from testgen.data.instruction_params import generate_random_params
from testgen.data.test_data import TestData
from testgen.instruction_formatters import format_single_test
from testgen.utils.edges import MEMORY_EDGES


@add_coverpoint_generator("cp_memval")
def make_memval(instr_name: str, instr_type: str, coverpoint: str, test_data: TestData) -> list[str]:
    """Generate tests for memory value edge cases."""
    if coverpoint == "cp_memval_byte":
        memvals = MEMORY_EDGES.byte
    elif coverpoint == "cp_memval_hword":
        memvals = MEMORY_EDGES.hword
    elif coverpoint == "cp_memval_word":
        memvals = MEMORY_EDGES.word
    elif coverpoint == "cp_memval_double":
        memvals = MEMORY_EDGES.double
    else:
        raise ValueError(f"Unknown cp_memval coverpoint variant: {coverpoint} for {instr_name}")

    test_lines: list[str] = []
    for val in memvals:
        test_lines.append("")
        params = generate_random_params(test_data, instr_type, allow_x0=False, rs2val=val)
        desc = f"{coverpoint} (memory value = {val:#x})"
        test_lines.append(format_single_test(instr_name, instr_type, test_data, params, desc))
        test_data.int_regs.return_registers(params.used_int_regs)

    return test_lines

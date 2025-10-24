# testgen/coverpoints/cp_uimm.py
"""cp_uimm coverpoint generator."""

from testgen.coverpoints.coverpoints import add_coverpoint_generator
from testgen.data.instruction_params import generate_random_params
from testgen.data.test_data import TestData
from testgen.instruction_formatters import format_single_test


@add_coverpoint_generator("cp_uimm")
def make_cp_uimm(instr_name: str, instr_type: str, coverpoint: str, test_data: TestData) -> list[str]:
    """Generate tests for unsigned immediate values."""
    if coverpoint == "cp_uimm":
        uimm_vals = range(0, test_data.xlen)
    elif coverpoint.endswith("_5"):
        uimm_vals = range(0, 32)
    else:
        raise ValueError(f"Unknown cp_uimm coverpoint variant: {coverpoint} for {instr_name}")

    test_lines: list[str] = []
    for uimm in uimm_vals:
        test_lines.append("")
        params = generate_random_params(test_data, instr_type, immval=uimm)
        desc = f"{coverpoint}: imm={uimm}"
        test_lines.append(format_single_test(instr_name, instr_type, test_data, params, desc))
        test_data.int_regs.return_registers(params.used_int_regs)

    return test_lines

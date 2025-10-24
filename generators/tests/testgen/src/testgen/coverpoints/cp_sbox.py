# testgen/coverpoints/cp_sbox.py
"""cp_sbox coverpoint generator."""

from testgen.coverpoints.coverpoints import add_coverpoint_generator
from testgen.data.instruction_params import generate_random_params
from testgen.data.test_data import TestData
from testgen.instruction_formatters import format_single_test


@add_coverpoint_generator("cp_sbox")
def make_cp_sbox(instr_name: str, instr_type: str, coverpoint: str, test_data: TestData) -> list[str]:
    """Generate tests to exercise sbox."""
    if coverpoint == "cp_sbox":
        sbox_vals = range(256)
    else:
        raise ValueError(f"Unknown cp_sbox coverpoint variant: {coverpoint} for {instr_name}")

    test_lines: list[str] = []
    for sbox in sbox_vals:
        # repeat sbox value in each byte
        if test_data.xlen == 32:
            s = sbox | sbox << 8 | sbox << 16 | sbox << 24
        else:  # test_data.xlen == 64
            s = sbox | sbox << 8 | sbox << 16 | sbox << 24 | sbox << 32 | sbox << 40 | sbox << 48 | sbox << 56

        test_lines.append("")
        params = generate_random_params(test_data, instr_type, allow_x0=False, rs1val=s, rs2val=s)
        desc = f"{coverpoint} = {sbox}"
        test_lines.append(format_single_test(instr_name, instr_type, test_data, params, desc))
        test_data.int_regs.return_registers(params.used_int_regs)

    return test_lines

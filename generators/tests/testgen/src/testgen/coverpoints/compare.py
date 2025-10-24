# testgen/coverpoints/compare.py
"""Compare register coverpoint generators (cmp_rd_rs1, cmp_rd_rs2, cmp_rs1_rs2, cmp_rd_rs1_rs2)."""

from testgen.coverpoints.coverpoints import add_coverpoint_generator
from testgen.data.instruction_params import generate_random_params
from testgen.data.test_data import TestData
from testgen.instruction_formatters import format_single_test


@add_coverpoint_generator("cmp_rd_rs1")
def make_cmp_rd_rs1(instr_name: str, instr_type: str, coverpoint: str, test_data: TestData) -> list[str]:
    """Generate tests where rd = rs1."""
    # Determine which rd registers to test based on coverpoint variant
    if coverpoint == "cmp_rd_rs1":
        regs = range(test_data.int_regs.reg_count)
    elif coverpoint.endswith("_nx0"):
        regs = range(1, test_data.int_regs.reg_count)  # Exclude x0
    elif coverpoint.endswith("_c"):
        regs = range(8, 16)  # x8-x15 for compressed instructions
    else:
        raise ValueError(f"Unknown cmp_rd_rs1 coverpoint variant: {coverpoint} for {instr_name}")

    test_lines: list[str] = []

    # Generate tests
    for reg in regs:
        test_lines.append(test_data.int_regs.consume_registers([reg]))
        params = generate_random_params(test_data, instr_type, rd=reg, rs1=reg)
        desc = f"{coverpoint} (Test rd = rs1 = x{reg})"
        test_lines.append(format_single_test(instr_name, instr_type, test_data, params, desc))
        test_data.int_regs.return_registers(params.used_int_regs)

    return test_lines


@add_coverpoint_generator("cmp_rd_rs2")
def make_cmp_rd_rs2(instr_name: str, instr_type: str, coverpoint: str, test_data: TestData) -> list[str]:
    """Generate tests where rd = rs2."""
    # Determine which rd registers to test based on coverpoint variant
    if coverpoint == "cmp_rd_rs2":
        regs = range(test_data.int_regs.reg_count)
    elif coverpoint.endswith("_nx0"):
        regs = range(1, test_data.int_regs.reg_count)  # Exclude x0
    elif coverpoint.endswith("_c"):
        regs = range(8, 16)  # x8-x15 for compressed instructions
    else:
        raise ValueError(f"Unknown cmp_rd_rs2 coverpoint variant: {coverpoint} for {instr_name}")

    test_lines: list[str] = []

    # Generate tests
    for reg in regs:
        test_lines.append(test_data.int_regs.consume_registers([reg]))
        params = generate_random_params(test_data, instr_type, rd=reg, rs2=reg)
        desc = f"{coverpoint} (Test rd = rs2 = x{reg})"
        test_lines.append(format_single_test(instr_name, instr_type, test_data, params, desc))
        test_data.int_regs.return_registers(params.used_int_regs)

    return test_lines


@add_coverpoint_generator("cmp_rs1_rs2")
def make_cmp_rs1_rs2(instr_name: str, instr_type: str, coverpoint: str, test_data: TestData) -> list[str]:
    """Generate tests where rs1 = rs2."""
    # Determine which rd registers to test based on coverpoint variant
    if coverpoint == "cmp_rs1_rs2":
        regs = range(test_data.int_regs.reg_count)
    elif coverpoint.endswith("_nx0"):
        regs = range(1, test_data.int_regs.reg_count)  # Exclude x0
    elif coverpoint.endswith("_c"):
        regs = range(8, 16)  # x8-x15 for compressed instructions
    else:
        raise ValueError(f"Unknown cmp_rs1_rs2 coverpoint variant: {coverpoint} for {instr_name}")

    test_lines: list[str] = []

    # Generate tests
    for reg in regs:
        test_lines.append(test_data.int_regs.consume_registers([reg]))
        params = generate_random_params(test_data, instr_type, rs1=reg, rs2=reg)
        desc = f"{coverpoint} (Test rs1 = rs2 = x{reg})"
        test_lines.append(format_single_test(instr_name, instr_type, test_data, params, desc))
        test_data.int_regs.return_registers(params.used_int_regs)

    return test_lines


@add_coverpoint_generator("cmp_rd_rs1_rs2")
def make_cmp_rd_rs1_rs2(instr_name: str, instr_type: str, coverpoint: str, test_data: TestData) -> list[str]:
    """Generate tests where rd = rs1 = rs2."""
    # Determine which rd registers to test based on coverpoint variant
    if coverpoint == "cmp_rd_rs1_rs2":
        regs = range(test_data.int_regs.reg_count)
    elif coverpoint.endswith("_nx0"):
        regs = range(1, test_data.int_regs.reg_count)  # Exclude x0
    else:
        raise ValueError(f"Unknown cmp_rd_rs1_rs2 coverpoint variant: {coverpoint} for {instr_name}")

    test_lines: list[str] = []

    # Generate tests
    for reg in regs:
        test_lines.append(test_data.int_regs.consume_registers([reg]))
        params = generate_random_params(test_data, instr_type, rd=reg, rs1=reg, rs2=reg)
        desc = f"{coverpoint} (Test rd = rs1 = rs2 = x{reg})"
        test_lines.append(format_single_test(instr_name, instr_type, test_data, params, desc))
        test_data.int_regs.return_registers(params.used_int_regs)

    return test_lines

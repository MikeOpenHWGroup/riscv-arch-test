# testgen/coverpoints/cp_align.py
"""cp_align coverpoint generator."""

from testgen.coverpoints.coverpoints import add_coverpoint_generator
from testgen.data.instruction_params import generate_random_params
from testgen.data.test_data import TestData
from testgen.instruction_formatters import format_instruction
from testgen.utils.common import load_int_reg


@add_coverpoint_generator("cp_align")
def make_align(instr_name: str, instr_type: str, coverpoint: str, test_data: TestData) -> list[str]:
    """Generate tests for alignment coverpoints."""
    if coverpoint == "cp_align_byte":
        alignments = [0, 1, 2, 3, 4, 5, 6, 7]
    elif coverpoint == "cp_align_hword":
        alignments = [0, 2, 4, 6]
    elif coverpoint == "cp_align_word":
        alignments = [0, 4]
    else:
        raise ValueError(f"Unknown cp_align coverpoint variant: {coverpoint} for {instr_name}")

    test_lines: list[str] = []
    test_lines = []
    for alignment in alignments:
        params = generate_random_params(test_data, instr_type, immval=alignment)
        assert params.rs2 is not None and params.rs2val is not None
        test_lines.extend(
            [
                f"# {coverpoint}: imm[2:0]={alignment:03b}",
                load_int_reg("rs2", params.rs2, params.rs2val, test_data),
                f"LA(x{params.rs1}, scratch) # load base address",
                f"SREG x{params.rs2}, {params.immval}(x{params.rs1}) # store test value to memory",
            ]
        )
        # Don't use default instruction setup lines to avoid correcting offset
        _, test_specific_lines, check_lines = format_instruction(instr_name, instr_type, test_data, params)
        test_lines.append(test_specific_lines)
        test_lines.append(check_lines)
        test_lines.append("")  # blank line between tests
        test_data.int_regs.return_registers(params.used_int_regs)

    return test_lines

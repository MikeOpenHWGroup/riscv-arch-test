# testgen/instruction_formatters/csr_type.py

from testgen.data.instruction_params import InstructionParams
from testgen.data.test_data import TestData
from testgen.instruction_formatters.instruction_formatters import add_instruction_formatter
from testgen.utils.common import load_int_reg, write_sigupd


@add_instruction_formatter("CSR")
def format_csr_type(
    instr_name: str, test_data: TestData, params: InstructionParams
) -> tuple[list[str], list[str], list[str]]:
    """Format CSR-type instruction."""
    assert params.rs1 is not None and params.rs1val is not None
    assert params.rs2 is not None and params.rs2val is not None
    assert params.rd is not None
    csr = "mscratch"  # Default CSR for testing
    setup = [
        load_int_reg("rs1", params.rs1, params.rs1val, test_data),
        load_int_reg("temp reg", params.rs2, params.rs2val, test_data),
        f"csrw {csr}, x{params.rs2} # setup CSR with random value",
    ]
    test = [
        f"{instr_name} x{params.rd}, {csr}, x{params.rs1} # perform operation",
    ]
    check = [
        write_sigupd(params.rd, test_data, "int"),
        f"csrr x{params.rs2}, {csr} # read back CSR to check updated value",
        write_sigupd(params.rs2, test_data, "int"),
    ]
    return (setup, test, check)

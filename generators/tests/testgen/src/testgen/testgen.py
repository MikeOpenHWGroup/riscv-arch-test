#!/usr/bin/env python3

##################################
# testgen.py
#
# jcarlin@hmc.edu 5 Oct 2025
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# Generate directed tests for functional coverage
##################################

from pathlib import Path
from typing import Annotated

import typer

from testgen.coverpoints import generate_tests_for_coverpoint
from testgen.data.test_data import TestData
from testgen.utils.common import get_sig_space
from testgen.utils.templates import insert_setup_template
from testgen.utils.testplans import get_extensions, read_testplan

# CLI interface setup
testgen_app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@testgen_app.command()
def generate_all_tests(
    testplan_dir: Annotated[
        Path, typer.Argument(exists=True, file_okay=False, help="Directory containing testplan CSV files")
    ],
    output_test_dir: Annotated[
        Path, typer.Option("--output_test_dir", "-o", help="Directory to output generated tests")
    ] = Path("tests"),
    extensions: Annotated[
        str,
        typer.Option(
            "--extensions", "-e", help="Comma-separated list of extensions to generate tests for (default: all)"
        ),
    ] = "all",
) -> None:
    """
    Generate riscv-arch-test tests from testplan CSV files.
    """
    # Get list of extensions
    extensions_from_testplans = get_extensions(testplan_dir)
    extension_list: list[str] = []
    if extensions == "all":
        extension_list = extensions_from_testplans
    else:
        for ext in extensions.split(","):
            ext = ext.strip()
            if ext not in extensions_from_testplans:
                raise ValueError(f"Extension {ext} not found in testplans at {testplan_dir}")
            extension_list.append(ext)

    # Generate tests for each extension, xlen, and E_ext combination
    for xlen in [32, 64]:
        for E_ext in [False]:  # TODO: Enable E tests
            for extension in sorted(extension_list):
                # Set extension-specific variables
                output_dir = output_test_dir / f"rv{xlen}{'e' if E_ext else ''}/{extension}"
                output_dir.mkdir(parents=True, exist_ok=True)
                flen = (
                    128
                    if extension in ["Q", "ZfaQ", "ZfhQ"]
                    else 64
                    if extension in ["D", "ZfaD", "ZfhD", "Zcd", "ZfaZfhD", "ZfhminD"]
                    else 32
                )
                print(f"Generating tests for {output_dir}")
                # Iterate through each instruction in extension
                instructions = read_testplan(testplan_dir / f"{extension}.csv")
                for instr_name, instr_data in sorted(instructions.items()):
                    # Skip instructions not valid for this xlen
                    if (xlen == 32 and not instr_data.rv32) or (xlen == 64 and not instr_data.rv64):
                        continue
                    test_data = TestData(xlen, flen, E_ext)
                    test_file = output_dir / f"{extension}-{instr_name}.S"
                    test_file_relative = str(test_file.relative_to(output_test_dir))

                    # Test header
                    test_lines = [insert_setup_template("testgen_header.S", xlen, extension, test_file_relative)]
                    # Enable floating point if needed
                    if "F" in extension or "D" in extension or "Q" in extension or "Zf" in extension:
                        test_lines.append("# set mstatus.FS to 01 to enable fp\nLI(t0,0x4000)\ncsrs mstatus, t0\n")

                    # Generate tests for this instruction
                    test_lines.append(
                        generate_tests_for_instruction(
                            instr_name, instr_data.instr_type, instr_data.coverpoints, test_data
                        )
                    )

                    # Test footer
                    test_lines.append(insert_setup_template("testgen_footer.S", xlen, extension, test_file_relative))

                    # Generate final test string with signature size
                    sig_words = get_sig_space(test_data)
                    test_string = "\n".join(test_lines).replace("@SIGUPD_COUNT_FROM_TESTGEN@", str(sig_words))

                    # Clean up test data
                    test_data.destroy()

                    # Write test file if different from existing file
                    if not (test_file.exists()) or test_file.read_text() != test_string:
                        test_file.write_text(test_string)
                        print(f"Updated {test_file}")


def generate_tests_for_instruction(
    instr_name: str, instr_type: str, coverpoints: list[str], test_data: TestData
) -> str:
    """
    Generate tests for a specific instruction based on its coverpoints.
    Each coverpoint generates multiple test cases.

    Args:
        instr_name: Instruction mnemonic (e.g., 'add', 'lw')
        instr_type: Instruction type (e.g., 'R', 'I', 'S')
        coverpoints: List of coverpoints for the instruction
        test_data: Test data context

    Returns:
        Generated test code as a string
    """
    # Extract relevant data
    test_lines: list[str] = []

    # Iterate through each coverpoint and generate tests
    for coverpoint in coverpoints:
        # If cp_asm_count is the only coverpoint, generate a trivial test:
        if coverpoint == "cp_asm_count":
            if len(coverpoints) == 1:
                test_lines.extend(["# Testcase cp_asm_count", f"{instr_name}"])
            continue
        else:
            test_lines.append(generate_tests_for_coverpoint(instr_name, instr_type, coverpoint, test_data))

    # Combine test lines into a single string
    return "\n".join(test_lines) + "\n"


def main() -> None:
    testgen_app()  # runs generate_tests() using Typer to fill in args


if __name__ == "__main__":
    main()

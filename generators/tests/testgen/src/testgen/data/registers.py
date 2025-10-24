##################################
# registers.py
#
# jcarlin@hmc.edu 5 October 2025
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
##################################

"""
Register management for cvw-arch-verif test generation.
"""

import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def select_registers(num_regs: int, reg_list: list[int]) -> list[int]:
    """Select a specified number of unique registers from a list of available registers."""
    if num_regs > len(reg_list):
        raise ValueError("Not enough registers available to select from.")

    selected_regs = random.sample(reg_list, num_regs)
    return selected_regs


class RegisterFile:
    """Class to represent a register file and provide methods to select registers."""

    def __init__(self, reg_count: int) -> None:
        self._reg_count = reg_count
        self.reg_list = list(range(reg_count))

    def __repr__(self) -> str:
        return f"Register File with the following registers available: {self.reg_list}"

    def destroy(self) -> None:
        """Clean up resources used by RegisterFile."""
        if len(self.reg_list) != self._reg_count:
            raise RuntimeError("Cannot destroy RegisterFile: some registers are still in use.")

    @property
    def reg_count(self) -> int:
        return self._reg_count

    def get_registers(
        self, num_regs: int, *, exclude_reg: list[int] | None = None, reg_range: list[int] | None = None
    ) -> list[int]:
        """Get a specified number of unique registers from the register file."""
        # Handle exclusions and range limitations)
        if exclude_reg is None:
            exclude_reg = []
        if reg_range is not None:
            exclude_reg += [reg for reg in self.reg_list if reg not in reg_range]
        available_regs = [reg for reg in self.reg_list if reg not in exclude_reg]
        # Select random registers and remove them from the available list
        selected_regs = select_registers(num_regs, available_regs)
        for reg in selected_regs:
            self.reg_list.remove(reg)
        logger.debug(
            f"Getting {num_regs} registers from available {available_regs}, excluding {exclude_reg}. Selected: {selected_regs}"
        )
        return selected_regs

    def get_register(self, *, exclude_reg: list[int] | None = None, reg_range: list[int] | None = None) -> int:
        """Get a single register from the register file."""
        return self.get_registers(1, exclude_reg=exclude_reg, reg_range=reg_range)[0]

    def return_registers(self, regs: list[int]) -> None:
        """Mark registers as available again."""
        self.reg_list.extend(regs)
        self.reg_list = list(set(self.reg_list))  # Ensure uniqueness
        self.reg_list.sort()
        logger.debug(f"Returned registers: {regs}. Available registers after return: {self.reg_list}")

    def return_register(self, reg: int) -> None:
        """Mark a single register as available again."""
        self.return_registers([reg])

    def consume_registers(self, regs: list[int]) -> str | None:
        """Mark registers as used/unavailable."""
        logger.debug(f"Consuming registers: {regs}")
        for reg in regs:
            if reg in self.reg_list:
                self.reg_list.remove(reg)
            else:
                raise ValueError(f"Register {reg} is already in use or is not available.")
        return None


class IntegerRegisterFile(RegisterFile):
    """
    Class to represent an integer register file.

    Automatically handles special registers like signature pointer and link register.
    """

    default_sig_reg = 3
    default_link_reg = 4
    link_regs = (4, 7, 12)  # Limit legal link/temp registers to simplify failure handler

    def __init__(self, e_register_file: bool = False) -> None:
        # Use default RegisterFile functions but set register count based on E
        reg_count = 16 if e_register_file else 32
        super().__init__(reg_count)
        # Default special registers
        self._sig_reg = 3
        self._link_reg = 4
        self._temp_reg = self._link_reg + 1  # temp register is always the next register after the link register
        super().consume_registers([self._sig_reg, self._link_reg, self._temp_reg])

    def destroy(self) -> None:
        self.return_registers([self._sig_reg, self._link_reg, self._temp_reg])
        super().destroy()

    # Access to special registers
    @property
    def sig_reg(self) -> int:
        return self._sig_reg

    @property
    def link_reg(self) -> int:
        return self._link_reg

    @property
    def temp_reg(self) -> int:
        return self._temp_reg

    def move_sig_reg(self, new_reg: int) -> str:
        """Move the signature register to a specified register.

        Args:
            new_reg: The register number to move the signature pointer to.

        Returns:
            The assembly code needed to move the value from the old register to the new one.
        """
        if new_reg == 0:
            raise ValueError("Cannot move signature register to x0.")

        old_sig_reg = self._sig_reg
        self.return_register(self._sig_reg)
        if new_reg in self.reg_list:
            self.consume_registers([new_reg])
        self._sig_reg = new_reg
        asm_code = f"mv x{self._sig_reg}, x{old_sig_reg} # move signature pointer register"
        return asm_code

    def reset_special_registers(self) -> str:
        """Reset special registers to their default locations.

        Returns:
            The assembly code needed to move the values back to the default registers.
        """
        asm_code = ""
        # Reset signature register
        if self._sig_reg != self.default_sig_reg:
            asm_code += self.move_sig_reg(self.default_sig_reg) + "\n"
        # Reset link and temp registers
        if self._link_reg != self.default_link_reg:
            old_link_reg = self._link_reg
            old_temp_reg = self._temp_reg
            self.return_register(self._link_reg)
            self.return_register(self._temp_reg)
            self._link_reg = 4
            self._temp_reg = 5
            # Use super to avoid recursive checking for special reg conflicts
            super().consume_registers([self._link_reg, self._temp_reg])
            asm_code += (
                f"mv x{self._link_reg}, x{old_link_reg} # reset link register to default\n"
                f"mv x{self._temp_reg}, x{old_temp_reg} # reset temp register to default\n"
            )
        if asm_code != "":
            asm_code = "# Reset special registers to default locations\n" + asm_code
        return asm_code

    def consume_registers(self, regs: list[int]) -> str:
        """Mark registers as used/unavailable, handling special register conflicts.

        If any of the requested registers conflict with special registers (sig_reg, link_reg),
        this method will automatically relocate the special registers and return the necessary
        assembly code to perform the move.
        """
        asm_code = ""

        # Check for conflicts with special registers
        sig_conflict = self._sig_reg in regs
        link_conflict = self._link_reg in regs
        temp_conflict = self._temp_reg in regs
        old_sig_reg = -1
        old_link_reg = -1
        old_temp_reg = -1

        # Return special registers to pool if they conflict
        if sig_conflict:
            old_sig_reg = self._sig_reg
            self.return_register(self._sig_reg)

        if link_conflict or temp_conflict:
            old_link_reg = self._link_reg
            old_temp_reg = self._temp_reg
            self.return_register(self._link_reg)
            self.return_register(self._temp_reg)

        # Consume requested registers
        super().consume_registers(regs)

        # Reallocate special registers to new locations
        if sig_conflict:
            self._sig_reg = self.get_register(exclude_reg=[0])
            asm_code += f"\nmv x{self._sig_reg}, x{old_sig_reg} # switch signature pointer register to avoid conflict with test\n"

        if link_conflict or temp_conflict:
            # Restrict link register to specific set
            available_link_regs = [reg for reg in self.link_regs if reg + 1 in self.reg_list]
            self._link_reg = self.get_register(reg_range=available_link_regs)
            self._temp_reg = self._link_reg + 1  # temp register is always the next register after the link register
            # Use super to avoid recursive checking for special reg conflicts
            super().consume_registers([self._temp_reg])
            asm_code += (
                f"\nmv x{self._link_reg}, x{old_link_reg} # switch link pointer register to avoid conflict with test\n"
                f"\nmv x{self._temp_reg}, x{old_temp_reg} # switch temp pointer register to avoid conflict with test\n"
            )

        return asm_code


class FloatRegisterFile(RegisterFile):
    """Class to represent a floating point register file."""

    def __init__(self) -> None:
        # There are always 32 floating point registers
        super().__init__(32)

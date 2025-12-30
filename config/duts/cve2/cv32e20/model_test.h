# model_test.h
# TrickBox macros implementation.
# Jordan Carlin jcarlin@hmc.edu December 2025
# Copyright (c) 2025 OpenHW Foundation
# SPDX-License-Identifier: BSD-3-Clause

#ifndef _CV32E20_RVMODEL_H
#define _CV32E20_RVMODEL_H

#mikepass: .string "PASS!"
#mikefail: .string "FAIL!"

#define RVMODEL_DATA_SECTION

##### STARTUP #####

#define RVMODEL_BOOT

##### TERMINATION #####
#  RVMODEL_IO_WRITE_STR(x1, x2, x3, "mikepass") \
#  RVMODEL_IO_WRITE_STR(x1, x2, x3, "mikefail") \

#define RVMODEL_HALT_PASS \
  li x18, 1              ;\
  li x17, 0x20000000     ;\
  sw x18,0(x17)          ;\
  wfi                    ;\

#define RVMODEL_HALT_FAIL \
  li x18, 2              ;\
  li x17, 0x20000000     ;\
  sw x18,0(x17)          ;\
  wfi                    ;\

##### IO #####

#define RVMODEL_IO_INIT(_R1, _R2, _R3)

# Prints a null-terminated string by writting each byte in the string
# to the address of the 'virtual printer'.
# A pointer to the string is passed in _STR_PTR.
# _R1, _R2, and _R3 can be used as temporary registers if needed.
# Do not modify any other registers (or make sure to restore them).
#define RVMODEL_IO_WRITE_STR(_R1, _R2, _R3, _STR_PTR) \
1:                           ;                        \
  lbu  _R1, 0(_STR_PTR)      ; /* Load byte */        \
  beqz _R1, 3f               ; /* Exit if null */     \
2:                           ;                        \
  la   _R2, 0x10000000       ; /* virtual printer */  \
  sw   _R1, 0(_R2)           ;                        \
  addi _STR_PTR, _STR_PTR, 1 ; /* Next char */        \
  j 1b                       ; /* Loop */             \
3:

##### Machine Interrupts #####

#define RVMODEL_SET_MEXT_INT

#define RVMODEL_CLR_MEXT_INT

#define RVMODEL_SET_MTIMER_INT

#define RVMODEL_CLR_MTIMER_INT

#define RVMODEL_SET_MTIMER_INT_SOON

#define RVMODEL_SET_MSW_INT

#define RVMODEL_CLR_MSW_INT

##### Supervisor Interrupts #####

#define RVMODEL_SET_SEXT_INT

#define RVMODEL_CLR_SEXT_INT

#define RVMODEL_SET_STIMER_INT

#define RVMODEL_CLR_STIMER_INT

#define RVMODEL_SET_STIMER_INT_SOON

#define RVMODEL_SET_SSW_INT

#define RVMODEL_CLR_SSW_INT

##### Hypervisor Interrupts #####

#define RVMODEL_WRITE_GEIP

#endif // _CV32E20_RVMODEL_H

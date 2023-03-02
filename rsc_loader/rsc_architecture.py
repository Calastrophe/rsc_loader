import struct
from typing import *
from enum import Enum
from binaryninja.log import log_info
from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import InstructionTextTokenType, BranchType
from binaryninja.lowlevelil import LowLevelILFunction


class RSCInstruction(Enum):
    HALT = 0
    LDAC = 1
    STAC = 2
    MVAC = 3
    MOVR = 4
    JMP = 5
    JMPZ = 6
    OUT = 7
    SUB = 8
    ADD = 9
    INC = 10
    CLAC = 11
    AND = 12
    OR = 13
    ASHR = 14
    NOT = 15

def disasm(data: bytes, size: int) -> Optional[Tuple[RSCInstruction, int, str]]:
    if (size >= 4 and size <= 8):
        instr = struct.unpack('i', data[:4])[0]
        match instr:
            case 1 | 2 | 5 | 6:
                operand = struct.unpack('i', data[4:])[0]
                return (RSCInstruction(instr).name, 8, operand)
            case 0 | 3 | 4 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15:
                return (RSCInstruction(instr).name, 4, "")
    else:
        return None

class RSC(Architecture):
    name = 'rsc'
    address_size = 4
    default_int_size = 4
    max_instr_length = 8
    regs = {
        'ACC': RegisterInfo('ACC', 4),
        'R' : RegisterInfo('R', 4),
        'IR' : RegisterInfo('IR', 4),
        'AR' : RegisterInfo('AR', 4),
        'DR' : RegisterInfo('DR', 4),
        'PC' : RegisterInfo('PC', 4),
        'OUTR' : RegisterInfo('OUTR', 4),
        'Z' : RegisterInfo('Z', 1),
        'S' : RegisterInfo('S', 1),
        'sp' : RegisterInfo('sp', 2)
    }

    # Why Binary Ninja, why?
    stack_pointer = 'sp'

    def get_instruction_info(self, data: bytes, addr: int) -> Optional[InstructionInfo]:
        values = disasm(data, len(data))
        if values is not None:
            name, length, operand = values
        else:
            return None
        res = InstructionInfo()
        res.length = length
        match name:
            case "JMP":
                assert(type(operand) == int)
                res.add_branch(BranchType.UnconditionalBranch, operand)
            case "JMPZ":
                assert(type(operand) == int)
                res.add_branch(BranchType.TrueBranch, operand)
                res.add_branch(BranchType.FalseBranch, addr+8)
        return res

    def get_instruction_text(self, data: bytes, addr: int) -> Optional[Tuple[List['function.InstructionTextToken'], int]]:
        values = disasm(data, len(data))
        if values is not None:
            name, length, operand = values
        else:
            return None
        operand = hex(operand) if operand else ""
        tokens = [InstructionTextToken(InstructionTextTokenType.TextToken, name), InstructionTextToken(InstructionTextTokenType.TextToken, "  "), InstructionTextToken(InstructionTextTokenType.TextToken, operand)]
        return tokens, length

    def get_instruction_low_level_il(self, data: bytes, addr: int, il: LowLevelILFunction) -> Optional[int]:
        return None
        



RSC.register()
log_info("Success, loaded!")
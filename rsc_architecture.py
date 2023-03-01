import struct
from typing import *
from enum import Enum
from binaryninja.log import log_info
from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import InstructionTextTokenType


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

class RSC(Architecture):
    name = 'rsc'
    address_size = 4 # May need to change
    default_int_size = 4
    instr_alignment = 1
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
        match len(data):
            case 4:
                ret_length = 4
                name = struct.unpack('i', data[:4])[0]
            case 8:
                ret_length = 8
                name, operand = struct.unpack('ii', data[:8])
            case _:
                return None
            
        res = InstructionInfo()
        res.length = ret_length
        return res

    def get_instruction_text(self, data: bytes, addr: int) -> Optional[Tuple[List['function.InstructionTextToken'], int]]:
        match len(data):
            case 4:
                ret_length = 4
                data = struct.unpack('i', data[:4])[0]
            case 8:
                ret_length = 8
                data, operand = struct.unpack('ii', data[:8])
        match data:
            case 1 | 2 | 5 | 6 :
                name, operand = RSCInstruction(data).name, str(operand)
            case 0 | 3 | 4 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 :
                name, operand = RSCInstruction(data).name, ""
            case _:
                return None
        tokens = [InstructionTextToken(InstructionTextTokenType.TextToken, name), InstructionTextToken(InstructionTextTokenType.TextToken, operand)]
        return tokens, ret_length
        



RSC.register()
log_info("Success, loaded!")
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

def disasm(data: bytes, size: int) -> Optional[Tuple[str, str]]:
    match size:
        case 8:
            instr = struct.unpack('i', data[:4])[0]
            match instr:
                case 1 | 2 | 5 | 6:
                    operand = struct.unpack('i', data[4:])[0]
                    return (instr, operand)
                case _:
                    return (instr, " ")
        case 4 | 5 | 6 | 7:
            instr = struct.unpack('i', data[:4])[0]
            match instr:
                case 0 | 3 | 4 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15:
                    return (instr, " ")
                case _:
                    return None
        case _:
            return None



## TODO: REFACTOR THIS CODE, HOLY MOLY
## NOTE: DO NOT USE THIS CODE FOR REFERENCE, IT IS HOT GARBAGE

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
        ## EVERYTHING IS 8 BYTES
        ## CUT OFF 4 BYTES AND IDENTIFY THE LENGTH OF THE INSTRUCTION
        ##
        name, operand = struct.unpack('ii', data[:8])
        res = InstructionInfo()
        match name:
            case 1 | 2 | 5 | 6:
                res.length = 8
            case 0 | 3 | 4 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15:
                res.length = 4
            case _:
                return None
        match name:
            case 5:
                assert(type(operand) == int)
                res.add_branch(BranchType.UnconditionalBranch, operand)
            case 6:
                assert(type(operand) == int)
                res.add_branch(BranchType.TrueBranch, operand)
                res.add_branch(BranchType.FalseBranch, addr+8)
            case _:
                pass
        return res

    def get_instruction_text(self, data: bytes, addr: int) -> Optional[Tuple[List['function.InstructionTextToken'], int]]:
        if len(data) <= 8:
            log_info(f"INSTR TEXT {str(data)} {str(len(data))}")
        if disasm(data, len(data)):
            data, operand = disasm(data, len(data))
        else:
            return None
        log_info(f"OUTPUT {data} {operand}")
        match data:
            case 1 | 2 | 5 | 6 :
                name, operand = RSCInstruction(data).name, hex(operand)
                ret_length = 8
            case 0 | 3 | 4 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 :
                name, operand = RSCInstruction(data).name, ""
                ret_length = 4
            case _:
                return None
        tokens = [InstructionTextToken(InstructionTextTokenType.TextToken, name), InstructionTextToken(InstructionTextTokenType.TextToken, "  "), InstructionTextToken(InstructionTextTokenType.TextToken, operand)]
        return tokens, ret_length

    def get_instruction_low_level_il(self, data: bytes, addr: int, il: LowLevelILFunction) -> Optional[int]:
        return None
        



RSC.register()
log_info("Success, loaded!")
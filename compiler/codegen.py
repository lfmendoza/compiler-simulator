from __future__ import annotations

from dataclasses import dataclass

from .tac import TACInstr, TACProgram


@dataclass(frozen=True)
class AssemblyProgram:
    instructions: list[str]


class RegisterAllocator:
    def __init__(self) -> None:
        self._counter = 0
        self._map: dict[str, str] = {}
        self._instructions: list[str] = []

    def _new_reg(self) -> str:
        self._counter += 1
        return f"R{self._counter}"

    def ensure_reg(self, value: str | int) -> str:
        if isinstance(value, int):
            reg = self._new_reg()
            self._instructions.append(f"LOADI {reg}, {value}")
            return reg
        if value in self._map:
            return self._map[value]
        reg = self._new_reg()
        self._map[value] = reg
        self._instructions.append(f"LOAD {reg}, {value}")
        return reg

    def bind(self, name: str, reg: str) -> None:
        self._map[name] = reg

    def emit(self, instruction: str) -> None:
        self._instructions.append(instruction)

    def instructions(self) -> list[str]:
        return self._instructions


def generate(tac: TACProgram) -> AssemblyProgram:
    allocator = RegisterAllocator()

    for instr in tac.instructions:
        _emit_instr(instr, allocator)

    return AssemblyProgram(instructions=allocator.instructions())


def _emit_instr(instr: TACInstr, allocator: RegisterAllocator) -> None:
    if instr.op == "ASSIGN":
        reg = allocator.ensure_reg(instr.arg1)  # type: ignore[arg-type]
        allocator.emit(f"STORE {instr.result}, {reg}")
        allocator.bind(instr.result, reg)
        return

    if instr.op in {"+", "*"}:
        left_reg = allocator.ensure_reg(instr.arg1)  # type: ignore[arg-type]
        if isinstance(instr.arg2, int):
            op = "ADDI" if instr.op == "+" else "MULI"
            allocator.emit(f"{op} {left_reg}, {instr.arg2}")
        else:
            right_reg = allocator.ensure_reg(instr.arg2)  # type: ignore[arg-type]
            op = "ADD" if instr.op == "+" else "MUL"
            allocator.emit(f"{op} {left_reg}, {right_reg}")
        allocator.bind(instr.result, left_reg)
        return

    raise ValueError(f"Unsupported TAC op: {instr.op}")

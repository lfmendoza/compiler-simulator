from __future__ import annotations

from dataclasses import dataclass

from .tac import TACInstr, TACProgram


@dataclass(frozen=True)
class OptimizationResult:
    program: TACProgram
    explanations: list[str]


def optimize(tac: TACProgram) -> OptimizationResult:
    explanations: list[str] = []
    instructions = list(tac.instructions)

    instructions, fold_explanations = _constant_folding(instructions)
    explanations.extend(fold_explanations)

    instructions, copy_explanations = _copy_propagation(instructions)
    explanations.extend(copy_explanations)

    return OptimizationResult(program=TACProgram(instructions), explanations=explanations)


def _constant_folding(instructions: list[TACInstr]) -> tuple[list[TACInstr], list[str]]:
    optimized: list[TACInstr] = []
    explanations: list[str] = []
    for instr in instructions:
        if instr.op in {"+", "*"} and isinstance(instr.arg1, int) and isinstance(instr.arg2, int):
            value = instr.arg1 + instr.arg2 if instr.op == "+" else instr.arg1 * instr.arg2
            optimized.append(TACInstr("ASSIGN", value, None, instr.result))
            explanations.append(
                f"Constant folding: {instr.arg1} {instr.op} {instr.arg2} -> {value}"
            )
        else:
            optimized.append(instr)
    return optimized, explanations


def _copy_propagation(instructions: list[TACInstr]) -> tuple[list[TACInstr], list[str]]:
    uses: dict[str, int] = {}
    defs: dict[str, int] = {}

    def count_use(arg: str | int | None) -> None:
        if isinstance(arg, str) and arg.startswith("t"):
            uses[arg] = uses.get(arg, 0) + 1

    for idx, instr in enumerate(instructions):
        if instr.op in {"+", "*"}:
            count_use(instr.arg1)
            count_use(instr.arg2)
            if instr.result.startswith("t"):
                defs[instr.result] = idx
        elif instr.op == "ASSIGN":
            count_use(instr.arg1)
            if instr.result.startswith("t"):
                defs[instr.result] = idx

    optimized = list(instructions)
    explanations: list[str] = []

    i = 0
    while i < len(optimized) - 1:
        current = optimized[i]
        next_instr = optimized[i + 1]
        if (
            next_instr.op == "ASSIGN"
            and isinstance(next_instr.arg1, str)
            and next_instr.arg1.startswith("t")
            and uses.get(next_instr.arg1, 0) == 1
            and defs.get(next_instr.arg1) == i
        ):
            optimized[i] = TACInstr(
                current.op, current.arg1, current.arg2, next_instr.result
            )
            explanations.append(
                f"Eliminated temp {next_instr.arg1} by writing directly to {next_instr.result}"
            )
            optimized.pop(i + 1)
            continue
        i += 1

    return optimized, explanations

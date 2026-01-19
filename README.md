# Compiler Simulator (CLI + Library)

![CI](https://github.com/lfmendoza/compiler-simulator/actions/workflows/ci.yml/badge.svg)

Simulates a compiler pipeline: lexical analysis, parsing, semantic checks, TAC,
machine code generation, and optimization.

## Quickstart

```bash
python -m pip install -e ".[dev]"
compiler-sim all entregable.md
```

## CLI

```bash
compiler-sim lex entregable.md
compiler-sim parse entregable.md
compiler-sim semantic entregable.md
compiler-sim tac entregable.md
compiler-sim codegen entregable.md
compiler-sim optimize entregable.md
```

JSON output:

```bash
compiler-sim all entregable.md --format json
```

## Library

```python
from compiler import compile_source

result = compile_source("int position = initial + velocity * 60;")
print(result.tac.instructions)
```

## Development

```bash
pre-commit install
pytest
nox -s lint
```

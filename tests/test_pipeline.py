from compiler.pipeline import compile_source


def test_pipeline_outputs():
    source = (
        "int initial = 1;"
        "int velocity = 2;"
        "int position = initial + velocity * 60;"
    )
    result = compile_source(source)
    assert result.diagnostics == []
    assert len(result.tac.instructions) >= 3
    assert len(result.assembly.instructions) >= 3
    assert len(result.optimized_assembly.instructions) >= 3

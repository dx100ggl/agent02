# tests/test_executor_argument_validation.py

def test_executor_argument_validation():
    from brain.c2.executor.executor import Executor
    from brain.c4.tools.builtin.search_tool import SearchTool

    exec = Executor(tools=None, memory=None)
    tool = SearchTool()

    # Validation is off by default
    assert exec.enable_argument_validation is False

    # Turn validation on
    exec.enable_argument_validation = True

    # Missing required argument should raise
    try:
        exec._validate_args(tool, {})
        assert False, "Expected validation error for missing 'query'"
    except Exception:
        pass

    # Correct argument should pass
    exec._validate_args(tool, {"query": "hello"})

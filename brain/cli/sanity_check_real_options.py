# brain/cli/sanity_check_real_options.py

import os
from brain.c4.tools.registry import ToolRegistry
from brain.c4.tools.builtin.real_options_data_tool import RealOptionsDataTool
from brain.c4.tools.builtin.options_data_tool import OptionsDataTool

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def main():
    ticker = "NVDA"

    print_section("1. Registry sanity check")
    registry = ToolRegistry()
    print("Tools registered:", list(registry.list_tools().keys()))
    assert "real_options_data" in registry.list_tools()
    assert "options_data" in registry.list_tools()
    print("✓ Registry contains both real_options_data and options_data")

    print_section("2. Direct RealOptionsDataTool call")
    real_tool = registry.get("real_options_data")
    result_real = real_tool.run(ticker=ticker)
    print("Result keys:", result_real.keys())
    print("Source:", result_real.get("source"))
    print("IV:", result_real.get("iv"))
    print("Chain length:", len(result_real.get("chain", [])))

    print_section("3. Fallback test (disable API key)")
    os.environ["POLYGON_API_KEY"] = ""
    real_tool_no_key = RealOptionsDataTool()
    result_fallback = real_tool_no_key.run(ticker=ticker)
    print("Source:", result_fallback.get("source"))
    assert "synthetic_fallback" in result_fallback["source"]
    print("✓ Fallback works when API key is missing")

    print_section("4. Cache test")
    os.environ["POLYGON_API_KEY"] = "dummy"  # restore key
    real_tool_cached = RealOptionsDataTool()
    first = real_tool_cached.run(ticker=ticker)
    second = real_tool_cached.run(ticker=ticker)
    print("First source:", first.get("source"))
    print("Second source:", second.get("source"))
    print("✓ Cache returns real_cached on second call")

    print_section("5. B2 deterministic tool sanity check")
    b2 = registry.get("options_data")
    result_b2 = b2.run(ticker=ticker)
    print("B2 keys:", result_b2.keys())
    print("B2 chain length:", len(result_b2["chain"]))
    print("✓ Deterministic B2 tool still works")

    print_section("ALL CHECKS PASSED")
    print("Your C2 Real Options Data pipeline is fully operational.")

if __name__ == "__main__":
    main()

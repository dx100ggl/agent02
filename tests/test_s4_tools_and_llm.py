# tests/test_s4_tools_and_llm.py

from __future__ import annotations

from brain.build import build_brain
from brain.c4.tools.registry import ToolRegistry


def test_s4_tool_registry_llm_defaults():
    brain = build_brain(use_lmstudio=False)
    tools: ToolRegistry = brain.tools

    assert tools.default_llm == "lmstudio_llm"
    llm_tool = tools.get("lmstudio_llm")
    assert hasattr(llm_tool, "run")

    # Simple echo behavior (stub or real)
    result = llm_tool.run({"text": "hello", "memory_context": ""})
    assert isinstance(result, dict)
    assert "answer" in result or "text" in result


def test_s4_memory_tools_registered():
    brain = build_brain(use_lmstudio=False)
    tools: ToolRegistry = brain.tools

    assert "write_memory" in tools.tools
    assert "search_memory" in tools.tools

    write_tool = tools.get("write_memory")
    search_tool = tools.get("search_memory")

    # Write
    content = "S4 memory tool test"
    write_res = write_tool.run(content=content, metadata={"tag": "s4_memory_tool"})
    assert isinstance(write_res, dict)
    assert write_res["content"] == content

    # Search
    results = search_tool.run(query="S4 memory tool test", top_k=5, metadata_filter={"tag": "s4_memory_tool"})
    assert isinstance(results, list)
    assert any(r["content"] == content for r in results)

from brain.c2.router.dynamic_router import DynamicRouter
from brain.c2.executor.executor import Executor
from brain.c4.tools.registry import ToolRegistry
from brain.llm.lmstudio_llm import LMStudioLLM
from brain.c3.memory.store import InMemoryStore
from brain.c3.memory.retriever import MemoryRetriever
from brain.c3.memory.memory_service import MemoryService
from brain.c4.synthesizer.synthesizer import Synthesizer


def test_router_basic():
    tools = ToolRegistry()
    llm = LMStudioLLM()
    synth = Synthesizer(llm)
    executor = Executor(tools=tools, synthesizer=synth, llm=llm)

    store = InMemoryStore()
    retriever = MemoryRetriever(store)
    memory = MemoryService(store, retriever)

    router = DynamicRouter(executor=executor, llm=llm, memory=memory)

    ctx = router.route("fundamentals for AAPL", ctx={})

    assert "steps" in ctx
    assert "final" in ctx

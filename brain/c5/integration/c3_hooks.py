# brain/c5/integration/c3_hooks.py


"""
C5 → C3 integration hooks.
Applies memory updates produced by the reflection engine.
"""

def apply_memory_updates(memory_engine, updates: dict):
    """
    Writes structured updates into long-term memory.

    Expected memory_engine interface:
        memory_engine.write(key: str, value: Any)
        memory_engine.update_namespace(ns: str, data: dict)
    """

    if not updates:
        return memory_engine

    for key, value in updates.items():
        # Namespace update (e.g., "tools", "planner", "skills")
        if isinstance(value, dict):
            memory_engine.update_namespace(key, value)
        else:
            memory_engine.write(key, value)

    return memory_engine

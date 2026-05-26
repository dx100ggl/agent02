# brain/c2/router/dynamic_router.py

class DynamicRouter:
    """
    Extremely simple router for C2.
    In C6, routing is intentionally minimal and can be extended later.
    """

    def route(self, state):
        # Always return "default" for now.
        # Future versions may inspect state, memory, or plan metadata.
        return "default"

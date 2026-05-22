#!/usr/bin/env bash
set -e

echo "Creating C4 brain skeleton..."

# Root
mkdir -p brain

# Core files
touch brain/__init__.py
touch brain/state.py
touch brain/orchestrator.py

# Router
mkdir -p brain/router
touch brain/router/__init__.py
touch brain/router/base.py
touch brain/router/dynamic_router.py

# Planner
mkdir -p brain/planner
touch brain/planner/__init__.py
touch brain/planner/base.py
touch brain/planner/adaptive_planner.py

# Executor
mkdir -p brain/executor
touch brain/executor/__init__.py
touch brain/executor/base.py
touch brain/executor/executor.py

# Tools
mkdir -p brain/tools
touch brain/tools/__init__.py
touch brain/tools/base.py
touch brain/tools/registry.py

# Built‑in tools
mkdir -p brain/tools/builtin
touch brain/tools/builtin/__init__.py
touch brain/tools/builtin/tool_x.py
touch brain/tools/builtin/tool_y.py

# Memory
mkdir -p brain/memory
touch brain/memory/__init__.py
touch brain/memory/base.py
touch brain/memory/store.py
touch brain/memory/retrieval.py

# Synthesizer
mkdir -p brain/synthesizer
touch brain/synthesizer/__init__.py
touch brain/synthesizer/synthesizer.py

echo "C4 skeleton created."

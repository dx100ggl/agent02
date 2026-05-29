#!/usr/bin/env bash
set -e

BASE="docs/brain-24/posters"

########################################
# Cortex Posters (Missing Ones)
########################################
mkdir -p $BASE/Cortex/C1
mkdir -p $BASE/Cortex/C3
mkdir -p $BASE/Cortex/C4

touch $BASE/Cortex/C1/brain-24-C1-immediate-cognition-poster.md
touch $BASE/Cortex/C3/brain-24-C3-self-directed-cognition-poster.md
touch $BASE/Cortex/C4/brain-24-C4-tool-augmented-cognition-poster.md

########################################
# Control Plane Posters
########################################
mkdir -p $BASE/Control-Plane/Router
mkdir -p $BASE/Control-Plane/Orchestrator
mkdir -p $BASE/Control-Plane/Unified

touch $BASE/Control-Plane/Router/brain-24-router-poster.md
touch $BASE/Control-Plane/Orchestrator/brain-24-orchestrator-poster.md
touch $BASE/Control-Plane/Unified/brain-24-control-plane-unified-poster.md

echo "Missing Brain-24 posters (C1, C3, C4, Control Plane) created successfully."

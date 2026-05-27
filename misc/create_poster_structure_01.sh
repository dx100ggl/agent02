#!/usr/bin/env bash
set -e

BASE="docs/brain-24/posters"

# Top-level groups
mkdir -p $BASE/Cortex
mkdir -p $BASE/Memory
mkdir -p $BASE/Skills
mkdir -p $BASE/Consolidation
mkdir -p $BASE/Cross-Organ

########################################
# Cortex Posters
########################################
mkdir -p $BASE/Cortex/C2
mkdir -p $BASE/Cortex/C5

touch $BASE/Cortex/C2/brain-24-C2-subsystem-poster.md
touch $BASE/Cortex/C5/brain-24-C5-reflective-cognition-poster.md

########################################
# Memory Posters
########################################
mkdir -p $BASE/Memory/Episodic
mkdir -p $BASE/Memory/Semantic
mkdir -p $BASE/Memory/Procedural
mkdir -p $BASE/Memory/Cross-Memory

touch $BASE/Memory/Episodic/brain-24-episodic-memory-poster.md
touch $BASE/Memory/Semantic/brain-24-semantic-memory-poster.md
touch $BASE/Memory/Procedural/brain-24-procedural-memory-poster.md
touch $BASE/Memory/Cross-Memory/brain-24-cross-memory-poster.md

########################################
# Skills Posters
########################################
mkdir -p $BASE/Skills/Skills-Organ
mkdir -p $BASE/Skills/Skill-Evaluation

touch $BASE/Skills/Skills-Organ/brain-24-skills-organ-poster.md
touch $BASE/Skills/Skill-Evaluation/brain-24-skill-evaluation-confidence-poster.md

########################################
# Consolidation Posters
########################################
mkdir -p $BASE/Consolidation/Engine

touch $BASE/Consolidation/Engine/brain-24-consolidation-engine-poster.md

########################################
# Cross-Organ Posters
########################################
mkdir -p $BASE/Cross-Organ/C2-Skills-Memory
mkdir -p $BASE/Cross-Organ/Memory-Skills-C2-Consolidation
mkdir -p $BASE/Cross-Organ/Learning-Stack

touch $BASE/Cross-Organ/C2-Skills-Memory/brain-24-C2-skills-memory-poster.md
touch $BASE/Cross-Organ/Memory-Skills-C2-Consolidation/brain-24-memory-skills-c2-consolidation-poster.md
touch $BASE/Cross-Organ/Learning-Stack/brain-24-learning-stack-unified-poster.md

echo "Brain-24 Learning Stack poster structure created successfully."

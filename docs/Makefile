# ============================================
# Brain‑24 Documentation Makefile
# ============================================

DOCS_DIR := brain-24
POSTERS_DIR := $(DOCS_DIR)/posters

# --------------------------------------------
# Default target
# --------------------------------------------
all: validate tree

# --------------------------------------------
# Validate directory structure
# --------------------------------------------
validate:
    @echo "Validating Brain‑24 documentation structure..."
    @test -d $(DOCS_DIR) || (echo "Missing: $(DOCS_DIR)/" && exit 1)
    @test -f $(DOCS_DIR)/README.md || (echo "Missing: $(DOCS_DIR)/README.md" && exit 1)
    @test -f $(DOCS_DIR)/SUMMARY.md || (echo "Missing: $(DOCS_DIR)/SUMMARY.md" && exit 1)
    @test -d $(POSTERS_DIR) || (echo "Missing: $(POSTERS_DIR)/" && exit 1)
    @echo "✓ Structure OK"

# --------------------------------------------
# Pretty directory tree
# --------------------------------------------
tree:
    @echo "Documentation tree:"
    @tree -I "node_modules|__pycache__"

# --------------------------------------------
# Markdown linting (requires markdownlint-cli)
# --------------------------------------------
lint:
    @echo "Running Markdown lint..."
    @markdownlint .

# --------------------------------------------
# Build diagrams (requires mmdc)
# --------------------------------------------
diagrams:
    @echo "Rendering Mermaid diagrams..."
    @find . -name "*.md" -exec grep -l "mermaid" {} \; | while read f; do \
        echo "Processing $$f"; \
    done

# --------------------------------------------
# Clean generated artifacts
# --------------------------------------------
clean:
    @echo "Cleaning generated files..."
    @find . -name "*.png" -delete
    @find . -name "*.svg" -delete
    @echo "✓ Clean"

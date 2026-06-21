# vean

`vean` (pronounced /viɲ/, like the French word *vigne*) is a modular data pipeline and vector indexing engine designed to extract, structure, and index formal mathematical knowledge from Lean 4 and Mathlib4.

The project aims to bridge the gap between formal logic and semantic vector search, providing a robust infrastructure for mathematical exploration, discovery, and tool integration.

## Key Features

- **AST-Based Extraction:** Parses Lean 4 source files to isolate mathematical entities (theorems, definitions, proofs, and accompanying docstrings) into discrete, structured data blocks.
- **Interchangeable Embedding Pipeline:** Implements a decoupled architecture allowing seamless swapping of embedding models—from standard NLP encoders targeting natural language descriptions to specialized models optimized for formal syntax.
- **Incremental Event-Driven Updates:** Built to track upstream Mathlib4 modifications via automated diff processing, ensuring the vector database remains up-to-date without complete re-indexing.

## Architecture & Workflow

1. **Ingest:** Tracks and pulls changes from upstream formal repositories.
2. **Parse:** Extracts logical components and metadata while maintaining structural dependency graphs.
3. **Embed:** Generates high-dimensional vectors via an abstract strategy pattern.
4. **Store:** Syncs vectors and rich metadata into a high-performance vector database.

## Getting Started

*(Documentation regarding local environment setup, Python virtual environments, and database initialization will be detailed as development progresses).*

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the [LICENSE](LICENSE) file for details.
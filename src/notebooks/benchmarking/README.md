# Benchmarking

Notebooks for agent performance evaluation and benchmarking.

## Contents

- `main.ipynb` - Benchmarking execution
- `analyze_results.ipynb` - Results analysis
- `llm_as_a_judge.ipynb` - LLM-based evaluation
- `sbert.ipynb` - SBERT similarity evaluation

## Evaluation Methods

- **LLM-as-a-Judge**: Uses an LLM to evaluate answer quality
- **SBERT Similarity**: Measures semantic similarity between answers
- **Performance Metrics**: Duration, token usage, error rates

## Note

⚠️ **Development Artifacts**: These notebooks contain results from the original development dataset and are preserved for reference. For current synthetic benchmark results, see `/src/scripts/benchmarks/`.

For evaluation methodology documentation, see `/src/notebooks/Evaluation/EVALUATION_METHODOLOGY.md`.

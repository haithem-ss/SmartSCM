# Scripts

Benchmarking and dataset generation scripts.

## Contents

### `benchmark.py`
Executes agent benchmarking tests. Runs queries from dataset, measures performance, and generates evaluation metrics.

### `generate_dataset.py`
Dataset generation utilities for creating synthetic test data.

### `run_tests.py`
Test execution script for running benchmark suites.

### `analyze_results.ipynb`
Notebook for analyzing benchmark results and generating performance reports.

### `benchmarks/`
Directory containing benchmark result files:
- `benchmark_results_Deepseek_default_reformulated.csv` - Sample results with synthetic data

### `runs/`
Execution logs and run artifacts from benchmark sessions.

## Usage

Run benchmarks:
```bash
python src/scripts/benchmark.py
```

Generate test dataset:
```bash
python src/scripts/generate_dataset.py
```

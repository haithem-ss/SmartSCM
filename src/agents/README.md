# Agents

Multi-agent system for natural language data analysis.

## Components

### `orchestrator.py`
Main orchestrator that coordinates all agents. Routes queries, manages workflow, and integrates planning, validation, and execution.

### `pandas_agent.py`
Executes pandas data analysis operations. Generates and runs Python code for data manipulation and analysis.

### `planning_validator_agent.py`
Creates execution plans and validates them before execution. Ensures query feasibility and plans multi-step operations.

### `custom_pandas_agent.py`
Enhanced pandas agent with custom prompting and RAG capabilities for improved performance.

## Architecture

```
User Query → Orchestrator → Planning Agent → Validator → Pandas Agent → Result
                    ↓
              Short-term Memory
```

## Usage

Agents are initialized and managed by the Streamlit application in `/src/streamlit/app.py`.

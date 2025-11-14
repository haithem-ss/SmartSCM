# SmartSCM Assistant 🤖

An AI-powered data analytics assistant built with LangChain and Streamlit. Transform natural language queries into automated pandas analysis using a multi-agent architecture.

## 📖 Project Blog

For a detailed walkthrough and insights about this project, read the blog post:
[SmartSCM: AI-powered Data Analytics Assistant](https://www.haithemsaida.engineer/en/blog/smartscm)

## 📋 Overview

This project demonstrates an intelligent multi-agent system that analyzes data and answers natural language questions. The system uses a coordinated architecture with planning, validation, and execution agents to process queries and generate insights.

**Key Capabilities:**
- Natural language to pandas code generation
- Automated data analysis and visualization
- Multi-step query planning and validation
- Context-aware conversation memory

## ✨ Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **Automated Analysis**: Pandas-powered data manipulation and statistical analysis
- **Smart Visualizations**: Automatic chart and graph generation
- **Multi-Agent System**: 
  - **Orchestrator**: Routes queries and manages workflow
  - **Planning Agent**: Creates execution plans for complex queries
  - **Validator Agent**: Validates plans before execution
  - **Pandas Agent**: Generates and executes Python/pandas code
- **Conversation Memory**: Maintains context across multi-turn interactions
- **Tool Integration**: Data loading, visualization, and documentation tools

## 🏗️ Architecture

### Project Structure

```
src/
├── agents/           # Agent implementations
│   ├── orchestrator.py
│   ├── pandas_agent.py
│   ├── planning_validator_agent.py
│   └── custom_pandas_agent.py
├── tools/            # Agent tools
│   ├── data_loader_tool.py
│   ├── data_vizualization_tool.py
│   └── data_documentation_tool.py
├── memory/           # Conversation context
├── streamlit/        # Web interface
│   └── app.py
├── final_data/       # Sample datasets
│   ├── merged_data.csv
│   ├── data_documentation.yaml
│   └── data/         # Daily CSV files
├── notebooks/        # Development notebooks
└── scripts/          # Benchmarking scripts
```

## 📝 Configuration

### Environment Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Add your API key:
```env
DEEPSEEK_API_KEY=your_api_key_here
BASE_URL=https://api.deepseek.com  # Optional
```

### Key Configuration Files

- **`.env`** - API keys and environment variables
- **`src/final_data/data_documentation.yaml`** - Data schema documentation
- **`src/paths.py`** - Path configurations

## 🛠️ Development

### Prerequisites

- Python 3.8+
- DeepSeek API key (or compatible LLM API)

### Installation

```bash
# Clone the repository
git clone https://github.com/haithem-ss/PFE-SCM.git
cd PFE-SCM

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API key

# Run the application
streamlit run src/streamlit/app.py
```

### Benchmarking

```bash
python src/scripts/benchmark.py
```

### Development Notebooks

Explore the development process in `/src/notebooks/`:
- **EDA/** - Data exploration
- **Evaluation/** - Evaluation methodology
- **benchmarking/** - Performance benchmarking
- **custom_pandas_agent/** - Agent development

Each directory has its own README with module-specific details.

# Streamlit Application

Web interface for the SmartSCM Assistant.

## Structure

### `app.py`
Main Streamlit application. Provides the chat interface, manages sessions, and coordinates agent interactions.

**Features**:
- Chat interface with message history
- Predefined query suggestions
- Real-time agent responses
- Visualization display

### `.streamlit/`
Streamlit configuration and static assets.

- `static/` - Generated charts and visualizations
- Configuration files for theming and settings

## Running

```bash
streamlit run src/streamlit/app.py
```

## Environment Variables

Required in `.env`:
- `DEEPSEEK_API_KEY` - API key for LLM access
- `BASE_URL` (optional) - Custom API endpoint

## Usage

1. Enter questions in the chat interface
2. Use predefined prompts for common queries
3. View results and visualizations in the chat

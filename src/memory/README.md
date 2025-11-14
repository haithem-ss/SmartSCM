# Memory

Short-term memory management for conversation context.

## Components

### `short_term_memory.py`
Manages conversation history and context for the agent system. Stores recent interactions to maintain continuity across multi-turn conversations.

## Features

- Conversation history tracking
- Context window management
- Memory persistence across queries
- Automatic cleanup of old entries

## Usage

Memory is automatically managed by the orchestrator and integrated into agent prompts to provide conversation context.

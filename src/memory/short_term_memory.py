from langchain.memory import ConversationBufferWindowMemory

agent_short_term_memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    return_messages=True,
    k=3, 
)

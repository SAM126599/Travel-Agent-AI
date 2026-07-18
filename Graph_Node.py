# Graph_Node.py
from langchain_core.messages import AIMessage


def chatbot(state):

    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }
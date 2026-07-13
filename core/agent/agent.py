"""
agent.py — LangGraph agent for HearMeOut.

Replaces the old fixed intent -> canned response pipeline with a real
tool-using agent that can look up orders, check accounts, and process
refunds against the mock SQLite database, while keeping multi-turn memory
per conversation (per customer call session).

Graph shape:

    START -> agent -> (tools? -> agent -> ...) -> END
              ^-----------------|

`agent` node: calls the LLM with the running message history + tool defs.
`tools` node: executes any tool calls the LLM requested, appends results.
Conditional edge loops back to `agent` until the LLM responds without
requesting a tool call, then the graph ends.

Multi-turn memory is handled by LangGraph's checkpointer (MemorySaver here,
swap for a persistent one like SqliteSaver/PostgresSaver in production) and
keyed by `thread_id` — one thread_id per active voice session.
"""

import os
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AnyMessage, SystemMessage

# .env lives at the project root (voicebot/.env), two levels up from this
# file (voicebot/core/agent/agent.py) — walk up explicitly rather than
# relying on the current working directory, since that changes depending on
# where you run the script from.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from core.agent.agent_tools import ALL_TOOLS
from core.agent.database import init_db

SYSTEM_PROMPT = """You are the voice assistant for HearMeOut, a customer support line.

You can look up order statuses, check customer accounts, and process refunds
using the tools available to you. Rules:

- Always confirm the customer's identity (ask for their email) before
  looking up account details or processing a refund, unless they've already
  given it earlier in this conversation.
- Before calling process_refund, briefly confirm with the customer that they
  want to proceed — state the order and amount first.
- Keep responses short and conversational — this is a spoken voice
  interface, not a chat window. Avoid long lists or markdown formatting.
- If a tool returns an error or "not found" result, explain that plainly to
  the customer and ask for clarification (e.g. correct order ID or email).
- Never make up order or account information — only state what the tools
  return.
"""


class AgentState(TypedDict):
    """Graph state: just the running message list, merged via add_messages."""
    messages: Annotated[list[AnyMessage], add_messages]


def build_agent(model_name: str = "llama-3.3-70b-versatile"):
    """Construct and compile the LangGraph agent. Returns a runnable graph.

    Using Groq's free hosted tier for now (OpenAI-compatible, fast, good
    tool-calling support). Swap to local Qwen/vLLM later by changing just
    this constructor — nothing else in the graph needs to change.
    """
    llm = ChatGroq(model=model_name, temperature=0)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: AgentState) -> AgentState:
        messages = state["messages"]
        # Prepend system prompt only if not already present in this run
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(ALL_TOOLS))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


def run_turn(app, user_input: str, thread_id: str) -> str:
    """Send one user utterance through the agent and return the reply text.

    `thread_id` should be stable per voice session (e.g. a session/call ID)
    so LangGraph's checkpointer retrieves the right conversation history for
    multi-turn memory.
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"messages": [{"role": "user", "content": user_input}]}, config)
    final_message = result["messages"][-1]
    return final_message.content


if __name__ == "__main__":
    # Quick manual smoke test (requires GROQ_API_KEY in the environment).
    init_db()
    if not os.environ.get("GROQ_API_KEY"):
        print("Set GROQ_API_KEY to run this smoke test. Skipping live call.")
    else:
        app = build_agent()
        session_id = "demo-session-1"
        for turn in [
            "Hi, I want to check on my order.",
            "My email is priya.sharma@example.com",
            "Can you refund order ord_1001? It arrived damaged.",
            "Yes, go ahead.",
        ]:
            print(f"USER: {turn}")
            reply = run_turn(app, turn, session_id)
            print(f"AGENT: {reply}\n")
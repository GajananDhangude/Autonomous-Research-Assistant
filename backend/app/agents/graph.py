from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from app.agents.states import ResearchState
from app.agents.nodes import planner_agent, research_agent, summarizer_agent, writer_agent
from app.agents.tools import search_tools, write_file
from app.agents.router import research_router
# import redis
# from langgraph.checkpoint.redis import RedisSaver


# redis_client = redis.Redis(host='localhost' , port=6379 , db=0)
# checkpointer = RedisSaver(redis_client=redis_client)
# checkpointer.setup()
# Initialize the graph with state
builder = StateGraph(ResearchState)

# Add nodes
builder.add_node("Planner", planner_agent)
builder.add_node("Researcher", research_agent)
builder.add_node("Summarizer", summarizer_agent)
builder.add_node("Writer", writer_agent)
builder.add_node("tools", ToolNode(search_tools))
builder.add_node("write_file", ToolNode(write_file))


builder.add_edge(START, "Planner")
builder.add_edge("Planner", "Researcher")


builder.add_conditional_edges(
    "Researcher",
    tools_condition, 
    {
        "tools": "tools",
        '__end__': "Summarizer"
    }
)

builder.add_edge("tools", "Researcher")
builder.add_edge("Summarizer", "Writer")


builder.add_conditional_edges(
    "Writer",
    tools_condition,
    {
        "tools": "write_file",
        '__end__': END
    }
)

builder.add_edge("write_file", END)


graph = builder.compile()


if __name__ == "__main__":

    config = {"configurable": {"thread_id": "test_run"}}

    for event in graph.stream(
        {"user_query": "Investigate the specific performance benchmarks of Google's 'Willow' quantum chip released in late 2025. Compare its error-correction capabilities to traditional superconducting qubits and summarize the potential impact on AI model training speed as of early 2026."},
        config
    ):
        for node, data in event.items():
            print(f"\n--- Node: {node} ---")
            if "messages" in data and data["messages"]:
                last_msg = data["messages"][-1]
                if hasattr(last_msg, 'content'):
                    print(f"Latest Message: {last_msg.content[:100]}...")
                if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                    print(f"Tool Calls: {len(last_msg.tool_calls)}")
            if "plan" in data:
                print(f"Plan: {data['plan'][:100]}...")
            if "notes" in data:
                print(f"Notes: {data['notes'][:100]}...")
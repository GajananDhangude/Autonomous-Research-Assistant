from app.agents.states import ResearchState

def research_router(state:ResearchState):

    last_message = state['messages'][-1]

    if hasattr(last_message , 'tool_calls') and last_message.tool_calls:
        return "tools"

    return "Summarizer"
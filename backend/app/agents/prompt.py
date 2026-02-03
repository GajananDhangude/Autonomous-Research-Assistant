from app.agents.states import ResearchState


def planner_prompt(user_query:str) -> str:
    """Generate a prompt for the planning agent."""
    PLANNER_PROMPT = f"""You are a Search Planning Agent for an autonomous research system.
    OBJECTIVE:
    Generate web search queries that will find the MOST relevant and recent information for the user query.
    Give only one query that has all information about user_query.
    User query: {user_query}
    Respond with the plan only, no extra commentary."""

    return PLANNER_PROMPT


def research_prompt(plan) -> str:
    """Generate a prompt for the research agent."""
    RESEARCH_PROMPT = f"""You are a research agent.
    You have access to tools to search_web and scrape_web:
    - Use search_web ONLY 1 time to find relevant URLs
    - Use scrap_web after search_web to scrape the content from the top URLs
    Research Plan:
    {plan}
    Execute the tools to gather information based on this plan."""
    return RESEARCH_PROMPT


def summarize_prompt(raw_data:str) -> str:
    """Generate a prompt for the summarizer agent."""
    SUMMARIZE_PROMPT = f"""You are a knowledge engineer.
    Transform this data into a FACT DATABASE with sections:
    - Claims
    - Metrics
    - Dates
    - Sources
    DO NOT summarize. Preserve verifiable facts.
    DATA:
    {raw_data}"""

    return SUMMARIZE_PROMPT



def writer_prompt(state:ResearchState) -> str:
    """Generate a prompt for the writer agent."""

    user_query = state.get('user_query', 'N/A')
    plan = state.get('plan', 'N/A')
    notes = state.get('notes', 'N/A')
    
    WRITER_PROMPT = f"""You are a technical writer.
    Your task is to write a clear, concise report based on the user query, 
    research plan, and research notes below.
    User query:
    {user_query}
    Plan:
    {plan}
    Notes:
    {notes}
    Write a well-structured report with sections where appropriate. 
    Be concise but thorough.
    After writing the report, use the save_report_to_file tool to save it with a descriptive filename."""
    
    return WRITER_PROMPT

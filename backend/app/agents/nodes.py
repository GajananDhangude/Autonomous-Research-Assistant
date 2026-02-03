
from app.agents.states import ResearchState
from app.agents.llm import llm , research_llm
from app.agents.prompt import *
from app.agents.tools import search_web , scrap_web , save_report_to_file
from langchain_core.messages import AIMessage
import re



def planner_agent(state:ResearchState) ->ResearchState:
    """Creates a research plan based on user query."""
    user_query = state['user_query']

    response = llm.invoke(planner_prompt(user_query))

    return {
        "plan":response.content,
    }
        


def research_agent(state:ResearchState) -> ResearchState:
    """The Researcher uses tools to gather data based on the plan."""

    plan = state['plan']
    messages = state.get('messages', [])

    search_call = 0
    scrape_call = 0
    urls_found = []

    for msg in messages:
        if hasattr(msg , 'tool_calls') and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc['name'] =='search_web':
                    search_call += 1
                elif tc['name'] == 'scrap_web':
                    scrape_call += 1

        
        if hasattr(msg , 'content') and 'URL:' in str(msg.content):
            found = re.findall(r'(https?://[^\s\n"\'<>]+)', str(msg.content))
            urls_found.extend(found)

    print(f" Search calls: {search_call}, Scrape calls: {scrape_call}, URLs found: {len(urls_found)}")

    if search_call == 0:
        # Step 1: Do the search
        print(" Step 1: Searching web...")
        llm_with_search = llm.bind_tools([search_web])
        
        prompt = f"""Use the search_web tool to search for: {plan}
Call the search_web tool with the search query."""
        
        response = llm_with_search.invoke(prompt)
        return {"messages": [response]}
    
    elif search_call >= 1 and scrape_call == 0 and urls_found:

        print(f" Step 2: Scraping {len(urls_found[:2])} URLs...")
        llm_with_scrape = llm.bind_tools([scrap_web])
        
        # Take top 3 URLs
        top_urls = urls_found[:2]
        
        prompt = f"""Use the scrap_web tool to scrape these URLs: {top_urls}
Call scrap_web with this list of URLs: {top_urls}"""
        
        response = llm_with_scrape.invoke(prompt)
        return {"messages": [response]}
    
    else:
        # Step 3: We're done
        print(" Research complete - moving to summarizer")
        return {
            "messages": [AIMessage(content="Research complete - gathered sufficient data")]
        }

def summarizer_agent(state:ResearchState) -> ResearchState:
    raw_data_parts = []
    
    for msg in state.get("messages", []):

        if hasattr(msg, 'type') and msg.type == 'tool':
            raw_data_parts.append(f"Tool Result:\n{msg.content}\n")
        
        elif hasattr(msg, 'content') and msg.content and isinstance(msg.content, str):
            if len(msg.content) > 200:
                raw_data_parts.append(str(msg.content))
    
    raw_data = "\n\n".join(raw_data_parts)
    

    if not raw_data.strip() or len(raw_data) < 100:
        raw_data = "No substantial research data was collected. Please try again with a different query."
    
    print(f" Summarizing {len(raw_data)} characters of data")

    response = research_llm.invoke(summarize_prompt(raw_data))

    # if isinstance(response.content , list):
    #     summary_text = "".join([block.get("text" , "") for block in response.content if block.get("type") == "text"])
    # else:
    #     summary_text = response.content

    return {
        "notes":response.content
    }


def writer_agent(state: ResearchState):
    """Consolidates research notes into a final, polished report."""
    
    llm_with_writer = research_llm.bind_tools([save_report_to_file])

    response = llm_with_writer.invoke(writer_prompt(state))

    print(f" Report generated: {len(response.content)} characters")
    return {
        "final_report":response.content,
        "messages":[response]
    }    
    
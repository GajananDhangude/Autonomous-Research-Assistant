import pathlib
from typing import List
from langchain_community.utilities import GoogleSerperAPIWrapper
from firecrawl import FirecrawlApp
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
load_dotenv()


REPORT_ROOT = pathlib.Path.cwd() / "Reports"


@tool
def search_web(query:str) -> str:
    """Finds URLs and snippets from Google based on a query.
    Args:
        query: The search query string   
    Returns:
        A list of search results with URLs, titles, and snippets
    """
    try:
        search = GoogleSerperAPIWrapper(k=2)

        responce = search.results(query)

        organic = responce.get("organic" , [])

        formated_results = []

        for i , result in enumerate(organic , 1):
            formated_results.append(
                f"{i}. {result.get('title' , 'N/A')}\n"
                f"   URL: {result.get('link', 'N/A')}\n"
                f"   Snippet: {result.get('snippet', 'N/A')}\n"
            )


        return "\n".join(formated_results)
    
    except Exception as e:
        return f"Error performing search: {str(e)}"


@tool
def scrap_web(urls:List[str]) -> str:
    """Scrapes a list of URLs and returns clean Markdown content."""

    app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

    results = []
    for url in urls[:3]:
        scrap_result = app.scrape(url, formats=["markdown"])
        # content = scrap_result.get("markdown" ,  "No content found.")
        content = scrap_result.markdown
        # metadata = scrape_result.get("metadata", {})
        
        # results.append(f"Source: {url}\nTitle: {metadata.get('title')}\n{content}")
        results.append(content)

    return "\n".join(results)

@tool
def save_report_to_file(content: str, filename: str):
    """
    Saves the final research report to a local markdown file.
    'filename' should end in .md and be descriptive of the topic.
    """
    os.makedirs("research_reports", exist_ok=True)
    
    # Clean the filename to prevent path traversal issues
    safe_filename = os.path.basename(filename)
    path = os.path.join("research_reports", safe_filename)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return f"Successfully saved report to {path}"


search_tools = [search_web , scrap_web]
write_file = [save_report_to_file]


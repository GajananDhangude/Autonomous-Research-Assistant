from typing import TypedDict , Annotated  , List
from langgraph.graph.message import add_messages
from pydantic import BaseModel , Field
from langchain_core.messages import HumanMessage , AIMessage




class ResearchState(TypedDict):
    user_query:str

    plan:str
    notes:str
    final_report:str
    messages:Annotated[list , add_messages]



class WriteSchema(BaseModel):
    content: str = Field(description="The final polished report in Markdown.")
    file_path: str = Field(description="Name of the file to save (e.g., 'report.md').")
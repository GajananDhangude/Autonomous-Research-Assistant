from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.5
)


research_llm = ChatGoogleGenerativeAI(
    model='gemini-3-flash-preview'
)
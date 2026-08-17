from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")

class AnalyzerState(TypedDict):
    raw_text:str
    safety_score: Annotated[dict[str,int]]
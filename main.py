import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
from typing import TypedDict

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("Missing GROQ_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile")


class PipelineState(TypedDict):
    raw_text:str
    edited_text:str
    script_text:str
    final_text: str
    

def editor_node(state:PipelineState)->dict:
    
    prompt = (
        "You are an expert copyeditor. Clean up the following raw text. "
        "Fix any grammatical errors, spelling mistakes, and smooth out the transition flow "
        "while keeping the core message intact. Return only the edited text.\n\n"
        f"Text:\n{state['raw_text']}"
    )
    
    response = llm.invoke(prompt)
    
    return {"edited_text": response.content}

def script_writer_node(state:PipelineState)->dict:
    
    prompt = (
        "You are a charismatic YouTube content creator. Take this edited text and transform "
        "it into a highly engaging, punchy, conversational video script hook. Make it sound "
        "like a real person speaking passionately. Return only the script content.\n\n"
        f"Edited Text:\n{state['edited_text']}"
    )
    
    response = llm.invoke(prompt)
    
    return {"script_text":response.content}

def translator_node(state:PipelineState)->dict:
    
    prompt = (
        "You are an expert content localizer for the Indian market. Take the following script "
        "and convert it into natural, flowing 'Hinglish'. Do not simply translate it sentence-by-sentence "
        "or repeat information. Alternating comfortably between Hindi and English phrases just like "
        "an intellectual tech educator would speak naturally on a live stream. Keep the energy high! "
        "Return only the final Hinglish text.\n\n"
        f"Script:\n{state['script_text']}"
    )
    
    response = llm.invoke(prompt)
    
    return {"final_text":response.content}


from langgraph.graph import StateGraph,START,END

graph = StateGraph(PipelineState)


graph.add_node("editornode",editor_node)
graph.add_node("scriptwriternode",script_writer_node)
graph.add_node("translatornode",translator_node)


graph.add_edge(START,"editornode")
graph.add_edge("editornode","scriptwriternode")
graph.add_edge("scriptwriternode","translatornode")
graph.add_edge("translatornode",END)

app= graph.compile()

response = app.invoke({"raw_text":"Claude just released it fable model and it mindblowing as people are saying. It is a great model for text generation and it can be used for various applications. I am excited to see what people will create with it.Even the us government order to ban it for outsiders"})

print(response["final_text"])
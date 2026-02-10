import os
from typing import List, TypedDict
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from tavily import TavilyClient
from langgraph.graph import StateGraph, END

load_dotenv()

# --- Setup ---
# Model set to llama3.2:3b as requested
llm = OllamaLLM(model="llama3.2:3b")
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# --- State Definition ---
class AgentState(TypedDict):
    question: str
    plan: List[str]
    evidence: List[dict]
    section_texts: List[str]
    answer: str
    feedback: str
    score: int
    revision_count: int

# --- Nodes ---

def planner_node(state: AgentState):
    print("--- PLANNING ---")
    feedback_text = f"Feedback: {state.get('feedback', 'None')}"
    prompt = f"Create a clear list of section titles to answer: {state['question']}. {feedback_text}. Return titles only, one per line."
    response = llm.invoke(prompt)
    sections = [s.strip("- ").strip() for s in response.splitlines() if s.strip()]
    return {"plan": sections, "revision_count": state.get("revision_count", 0) + 1}

def research_node(state: AgentState):
    print("--- RESEARCHING ---")
    if state.get("evidence"):
        return {"evidence": state["evidence"]}
    
    results = tavily.search(query=state["question"], max_results=4)
    evidence = [
        {
            "title": r["title"], 
            "content": r["content"],
            "url": r.get("url", "#") 
        } 
        for r in results["results"]
    ]
    return {"evidence": evidence}

def worker_node(state: AgentState):
    print("--- WRITING SECTIONS ---")
    evidence_text = "\n".join([f"- {e['content']}" for e in state["evidence"]])
    texts = []
    for section in state["plan"]:
        prompt = f"Write a concise section for '{section}' using: {evidence_text}. Avoid repetition."
        texts.append(llm.invoke(prompt))
    return {"section_texts": texts}

def synthesizer_node(state: AgentState):
    print("--- SYNTHESIZING ---")
    combined = ""
    for title, text in zip(state["plan"], state["section_texts"]):
        combined += f"\n### {title}\n{text}\n"
    
    prompt = f"Synthesize this into a final technical answer. Remove redundancy:\n{combined}"
    return {"answer": llm.invoke(prompt)}

def evaluator_node(state: AgentState):
    print("--- EVALUATING ---")
    prompt = f"Rate this answer 1-10 on completeness and clarity. Question: {state['question']}\nAnswer: {state['answer']}\nReturn ONLY the number."
    
    # 1. Removed .content (Ollama returns string directly)
    response = llm.invoke(prompt).strip() 
    
    # 2. Extract only the FIRST digit found (e.g., "7" from "Score: 7/10")
    import re
    digits = re.findall(r'\d+', response)
    score = int(digits[0]) if digits else 5
    
    # 3. Safety check to keep it 1-10
    if score > 10: score = 10 
    
    return {"score": score, "feedback": f"Current score is {score}. Improve depth if low."}
        
    return {"score": score, "feedback": f"Current score is {score}. Improve depth if low."}
# --- Graph Logic ---
def should_continue(state: AgentState):
    if state["score"] >= 7 or state["revision_count"] >= 3:
        return "end"
    else:
        return "replan"

workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", research_node)
workflow.add_node("writer", worker_node)
workflow.add_node("synthesizer", synthesizer_node)
workflow.add_node("evaluator", evaluator_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "synthesizer")
workflow.add_edge("synthesizer", "evaluator")
workflow.add_conditional_edges("evaluator", should_continue, {"replan": "planner", "end": END})

app = workflow.compile()

def run_local_agent(question: str) -> dict:
    inputs = {"question": question, "revision_count": 0, "evidence": [], "section_texts": []}
    return app.invoke(inputs)
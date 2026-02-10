import streamlit as st
import os
from langgraph_agent import run_local_agent

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Autonomous Research Agent",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------
# STYLING (Identical to HF Version)
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a, #1a1033);
        color: #e5e7eb;
    }

    h1, h2, h3 {
        color: #c4b5fd !important;
    }

    /* Text input */
    textarea {
        background-color: #111827 !important;
        color: #e5e7eb !important;
        border-radius: 10px !important;
        border: 1px solid #312e81 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #7c3aed, #9333ea);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6em 1.4em;
        font-weight: 600;
        font-size: 16px;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #6d28d9, #7e22ce);
    }

    /* Status card */
    .status-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #1e1b4b;
        border: 1px solid #4338ca;
        margin-bottom: 20px;
    }

    /* Sticky Footer */
    .footer {
        position: fixed;
        left: 21rem; /* sidebar width */
        bottom: 12px;
        width: calc(100% - 21rem);
        color: #9ca3af;
        text-align: center;
        padding: 6px 0;
        font-size: 14px;
        z-index: 999;
        background: transparent;
    }

    /* Prevent content from hiding behind footer */
    .block-container {
        padding-bottom: 80px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🤖 Autonomous Research Agent")
st.markdown("""
This agent doesn't just "chat." It **plans**, **researches** via Tavily, 
**writes** sections, and **evaluates** its own work using an iterative LangGraph loop.
""")

with st.sidebar:
    st.header("Agent Configuration")
    # Updated text as per your request
    st.info("Running via **Ollama (Llama 3.2:3b)**")
    st.divider()
    st.markdown("### How it works:")
    st.markdown("""
    1. **Planner**: Creates outline
    2. **Researcher**: Fetches web data
    3. **Writer**: Drafts sections
    4. **Evaluator**: Checks quality
    5. **Loop**: Repeats if score < 7
    """)
    st.divider()
    st.markdown("### Project by:")
    st.markdown(" **Furqan Ahmed**")
    st.markdown("""
        - [Check Github Repository](https://github.com/Furqan09Ahmed/autonomous-research-agent)
        - [Connect on Linkedin](https://www.linkedin.com/in/Furqan09Ahmed)
    """)

# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------
question = st.text_area(
    "Enter a technical question:",
    placeholder="e.g., Explain the difference between BM25 and Dense Retrieval in RAG systems...",
    height=100
)

run_button = st.button("🚀 Run Agentic Pipeline")

# --------------------------------------------------
# EXECUTION
# --------------------------------------------------
if run_button:
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        # Check for Tavily Key (Since Groq is no longer needed locally)
        if not os.getenv("TAVILY_API_KEY"):
            st.error("API Key missing! Please set TAVILY_API_KEY in your .env file.")
        else:
            with st.spinner("🤖 Agent is thinking... (Planning → Research → Writing → Evaluating)"):
                try:
                    # Calling the local function
                    result = run_local_agent(question)
                    
                    # --- DISPLAY RESULTS (Identical to HF Version) ---
                    st.success("Analysis Complete!")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("## 📝 Final Answer")
                        st.markdown(result["answer"])
                        
                    with col2:
                        st.markdown("## 📊 Agent Metadata")
                        st.write(f"**Final Score:** {result.get('score', 'N/A')}/10")
                        st.write(f"**Iterations:** {result.get('revision_count', 1)}")
                        
                        if result.get("evidence"):
                            st.markdown("### 📚 Sources Consulted")
                            for i, ev in enumerate(result["evidence"], 1):
                                st.markdown(f"{i}. [{ev['title']}]({ev['url']})")

                except Exception as e:
                    st.error(f"An error occurred: {e}")

# --------------------------------------------------
# FOOTER (Updated to mention Ollama)
# --------------------------------------------------
st.markdown(
    """
    <div class="footer">
        Developed by 
        <a href="https://FurqanAhmed.me" target="_blank" style="color: #c4b5fd; text-decoration: none;">
            Furqan Ahmed
        </a>
        | Built with LangGraph, Ollama, and Tavily
    </div>
    """,
    unsafe_allow_html=True
)
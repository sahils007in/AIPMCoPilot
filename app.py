import streamlit as st
from openai import OpenAI

# ---------------- Page Config ----------------
st.set_page_config(page_title="AI PM Copilot", page_icon="🚀")

st.title("🚀 AI Product Manager Copilot")
st.caption("Transform raw product thinking into structured artifacts.")

# ---------------- Session State ----------------
if "output" not in st.session_state:
    st.session_state.output = ""

if "client" not in st.session_state:
    st.session_state.client = None

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Configuration")

    api_key = st.text_input("OpenAI API Key", type="password")

    role = st.selectbox(
        "PM Role",
        ["Startup PM", "Agile Coach", "Technical PM"]
    )

    tone = st.selectbox(
        "Output Style",
        ["Concise", "Detailed"]
    )

    if api_key:
        st.session_state.client = OpenAI(api_key=api_key)

    st.markdown("---")
    st.markdown("Built by **Sahil Jain** 🚀")

# Guard
if not st.session_state.client:
    st.info("Enter OpenAI API key in sidebar.")
    st.stop()

client = st.session_state.client

# ---------------- Input Area ----------------
user_input = st.text_area(
    "Paste meeting notes, product ideas, or transcripts",
    height=200
)

# ---------------- Prompt Builder ----------------
def build_prompt(task):
    base_context = f"""
You are an experienced Product Manager.

PM Style: {role}
Response Style: {tone}

Input:
{user_input}
"""

    prompts = {
        "summary": "Create an executive summary.",
        "actions": "Extract clear action items with priority.",
        "prd": """Create a structured PRD:
- Problem
- Target Users
- Goals
- Success Metrics
- Features
- Risks""",
        "stories": """Generate Agile user stories:
Format:
As a...
I want...
So that...
Include acceptance criteria."""
    }

    return base_context + "\n\nTask:\n" + prompts[task]

# ---------------- LLM Call ----------------
def generate(task):
    prompt = build_prompt(task)

    with st.spinner("Generating..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

    return response.choices[0].message.content

# ---------------- Action Buttons ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Executive Summary"):
        st.session_state.output = generate("summary")

with col2:
    if st.button("Action Items"):
        st.session_state.output = generate("actions")

with col3:
    if st.button("Generate PRD"):
        st.session_state.output = generate("prd")

with col4:
    if st.button("User Stories"):
        st.session_state.output = generate("stories")

# ---------------- Output Panel ----------------
st.subheader("Output")

output_box = st.empty()

if st.session_state.output:
    output_box.markdown(st.session_state.output)

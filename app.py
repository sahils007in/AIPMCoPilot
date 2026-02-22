import streamlit as st
from openai import OpenAI

# ---------------- Page Config ----------------
st.set_page_config(page_title="AI PM Copilot", page_icon="🚀")

st.title("🚀 AI Product Manager Copilot")
st.caption("Transform raw product thinking into structured artifacts.")

# ---------------- Session State ----------------
if "client" not in st.session_state:
    st.session_state.client = None

if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False

if "outputs" not in st.session_state:
    st.session_state.outputs = {
        "summary": "",
        "actions": "",
        "prd": "",
        "stories": ""
    }

# ---------------- API Key Validation ----------------
def validate_openai_api_key(api_key):
    try:
        test_client = OpenAI(api_key=api_key)
        test_client.models.list()
        return True
    except:
        return False

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
        if validate_openai_api_key(api_key):
            st.session_state.client = OpenAI(api_key=api_key)
            st.session_state.api_key_valid = True
            st.success("✅ API key valid")
        else:
            st.session_state.api_key_valid = False
            st.error("❌ Invalid API key")

    st.markdown("---")
    st.markdown("Built by **Sahil Jain** 🚀")

# Guard
if not st.session_state.api_key_valid:
    st.info("👈 Enter a valid OpenAI API key in sidebar.")
    st.stop()

client = st.session_state.client

# ---------------- Input ----------------
user_input = st.text_area(
    "Paste meeting notes, product ideas, or transcripts",
    height=200
)

# ---------------- Prompt Builder ----------------
def build_prompt(task):

    base_context = f"""
You are an expert Product Manager.

PM Style: {role}
Response Style: {tone}

Input:
{user_input}
"""

    prompts = {
        "summary": "Create an executive summary.",
        "actions": "Extract clear action items with priority.",
        "prd": """Create a structured Product Requirements Document:
- Problem
- Target Users
- Goals
- Success Metrics
- Features
- Risks""",
        "stories": """Generate Agile user stories:
As a...
I want...
So that...
Include acceptance criteria."""
    }

    return base_context + "\n\nTask:\n" + prompts[task]

# ---------------- LLM Generate ----------------
def generate(task):

    with st.spinner("Generating..."):

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":build_prompt(task)}],
            temperature=0.4
        )

    return response.choices[0].message.content

# ---------------- Action Buttons ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Executive Summary"):
        st.session_state.outputs["summary"] = generate("summary")

with col2:
    if st.button("Action Items"):
        st.session_state.outputs["actions"] = generate("actions")

with col3:
    if st.button("Generate PRD"):
        st.session_state.outputs["prd"] = generate("prd")

with col4:
    if st.button("User Stories"):
        st.session_state.outputs["stories"] = generate("stories")

# ---------------- Output Tabs (PRO UX) ----------------
st.subheader("Output")

tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Summary",
    "Action Items",
    "PRD",
    "User Stories"
])

with tab1:
    st.markdown(st.session_state.outputs["summary"])

with tab2:
    st.markdown(st.session_state.outputs["actions"])

with tab3:
    st.markdown(st.session_state.outputs["prd"])

with tab4:
    st.markdown(st.session_state.outputs["stories"])

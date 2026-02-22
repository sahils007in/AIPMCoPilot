import streamlit as st
from openai import OpenAI
import time

# ---------------- Page Config ----------------
st.set_page_config(page_title="AI PM Copilot", page_icon="🚀", layout="wide")

st.title("🚀 AI Product Manager Copilot")
st.caption("Transform raw product thinking into structured product artifacts.")

# ---------------- Session State ----------------
if "client" not in st.session_state:
    st.session_state.client = None

if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False

if "validated_key" not in st.session_state:
    st.session_state.validated_key = None

if "outputs" not in st.session_state:
    st.session_state.outputs = {
        "summary": "",
        "actions": "",
        "prd": "",
        "stories": ""
    }

if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# ---------------- API Validation ----------------
def validate_openai_api_key(api_key):
    try:
        test_client = OpenAI(api_key=api_key)
        test_client.models.list()
        return True
    except:
        return False

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙ Configuration")

    api_key = st.text_input("OpenAI API Key", type="password")

    role = st.selectbox(
        "PM Role",
        ["Startup PM", "Agile Coach", "Technical PM"]
    )

    tone = st.selectbox(
        "Output Style",
        ["Concise", "Detailed"]
    )

    if api_key and api_key != st.session_state.validated_key:
        with st.spinner("Validating API key..."):
            if validate_openai_api_key(api_key):
                st.session_state.client = OpenAI(api_key=api_key)
                st.session_state.api_key_valid = True
                st.session_state.validated_key = api_key
                st.success("✅ API key validated")
            else:
                st.session_state.api_key_valid = False
                st.error("❌ Invalid API key")

    st.markdown("---")
    st.markdown("Built by **Sahil Jain** 🚀")

# Guard
if not st.session_state.api_key_valid:
    st.info("👈 Enter a valid OpenAI API key to use the Copilot.")
    st.stop()

client = st.session_state.client

# ---------------- Input ----------------
user_input = st.text_area(
    "Paste meeting notes, product ideas, or transcripts",
    height=220
)

input_empty = not user_input.strip()

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
        "summary": "Create a clear executive summary with objectives and impact.",
        "actions": "Extract clear action items with priority levels.",
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

# ---------------- Generate ----------------
def generate(task):
    start_time = time.time()

    with st.spinner("Generating..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": build_prompt(task)}],
            temperature=0.4
        )

    duration = round(time.time() - start_time, 2)
    result = response.choices[0].message.content

    st.success(f"Generated in {duration} seconds")

    return result

# ---------------- Action Buttons ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Executive Summary", disabled=input_empty):
        st.session_state.outputs["summary"] = generate("summary")
        st.session_state.active_tab = 0

with col2:
    if st.button("Action Items", disabled=input_empty):
        st.session_state.outputs["actions"] = generate("actions")
        st.session_state.active_tab = 1

with col3:
    if st.button("Generate PRD", disabled=input_empty):
        st.session_state.outputs["prd"] = generate("prd")
        st.session_state.active_tab = 2

with col4:
    if st.button("User Stories", disabled=input_empty):
        st.session_state.outputs["stories"] = generate("stories")
        st.session_state.active_tab = 3

# ---------------- Output Section ----------------
st.markdown("---")
st.subheader("Output")

tabs = st.tabs([
    "Executive Summary",
    "Action Items",
    "PRD",
    "User Stories"
])

with tabs[0]:
    if st.session_state.outputs["summary"]:
        st.code(st.session_state.outputs["summary"], language="markdown")

with tabs[1]:
    if st.session_state.outputs["actions"]:
        st.code(st.session_state.outputs["actions"], language="markdown")

with tabs[2]:
    if st.session_state.outputs["prd"]:
        st.code(st.session_state.outputs["prd"], language="markdown")

with tabs[3]:
    if st.session_state.outputs["stories"]:
        st.code(st.session_state.outputs["stories"], language="markdown")

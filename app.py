import streamlit as st
from openai import OpenAI
import time

st.set_page_config(page_title="AI PM Copilot", page_icon="🚀", layout="wide")

st.title("🚀 AI Product Manager Copilot")
st.caption("Transform raw product thinking into structured product artifacts.")

# ---------------- SESSION STATE ----------------
defaults = {
    "client": None,
    "api_key_valid": False,
    "validated_key": None,
    "outputs": {"summary":"","actions":"","prd":"","stories":""},
    "active_view": "Executive Summary"
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- API VALIDATION ----------------
def validate_openai_api_key(key):
    try:
        OpenAI(api_key=key).models.list()
        return True
    except:
        return False

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Configuration")

    api_key = st.text_input("OpenAI API Key", type="password")

    role = st.selectbox("PM Role",
        ["Startup PM","Agile Coach","Technical PM"])

    tone = st.selectbox("Output Style",
        ["Concise","Detailed"])

    if api_key and api_key != st.session_state.validated_key:
        with st.spinner("Validating API key..."):
            if validate_openai_api_key(api_key):
                st.session_state.client = OpenAI(api_key=api_key)
                st.session_state.api_key_valid = True
                st.session_state.validated_key = api_key
                st.success("✅ API key valid")
            else:
                st.session_state.api_key_valid = False
                st.error("❌ Invalid API key")

    st.markdown("---")
    st.markdown("Built by **Sahil Jain** 🚀")

if not st.session_state.api_key_valid:
    st.info("Enter valid API key to continue.")
    st.stop()

client = st.session_state.client

# ---------------- INPUT ----------------
user_input = st.text_area("Paste product idea / meeting notes", height=220)
input_empty = not user_input.strip()

# ---------------- PROMPT BUILDER ----------------
def build_prompt(task, extra=None):

    base = f"""
You are an expert Product Manager.

PM Style: {role}
Response Style: {tone}

Input:
{user_input}
"""

    tasks = {
        "summary":"Create executive summary.",
        "actions":"Extract prioritized action items.",
        "prd":"Create full PRD: Problem, Users, Goals, Metrics, Features, Risks.",
        "stories":"Create Agile user stories with acceptance criteria."
    }

    refine = f"\nRefinement request: {extra}" if extra else ""

    return base + "\nTask:\n" + tasks[task] + refine

# ---------------- GENERATE ----------------
def generate(task, extra=None):
    start = time.time()

    with st.spinner("Generating..."):
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":build_prompt(task,extra)}]
        )

    duration = round(time.time()-start,2)
    st.success(f"Generated in {duration}s")

    return res.choices[0].message.content

# ---------------- ACTION BUTTONS ----------------
col1,col2,col3,col4 = st.columns(4)

with col1:
    if st.button("Executive Summary", disabled=input_empty):
        st.session_state.outputs["summary"]=generate("summary")
        st.session_state.active_view="Executive Summary"

with col2:
    if st.button("Action Items", disabled=input_empty):
        st.session_state.outputs["actions"]=generate("actions")
        st.session_state.active_view="Action Items"

with col3:
    if st.button("Generate PRD", disabled=input_empty):
        st.session_state.outputs["prd"]=generate("prd")
        st.session_state.active_view="PRD"

with col4:
    if st.button("User Stories", disabled=input_empty):
        st.session_state.outputs["stories"]=generate("stories")
        st.session_state.active_view="User Stories"

# ---------------- OUTPUT VIEW ----------------
st.markdown("---")
st.subheader("Workspace")

views = ["Executive Summary","Action Items","PRD","User Stories"]

selected = st.radio(
    "Select Output",
    views,
    horizontal=True,
    index=views.index(st.session_state.active_view)
)

output_key = {
    "Executive Summary":"summary",
    "Action Items":"actions",
    "PRD":"prd",
    "User Stories":"stories"
}[selected]

current_output = st.session_state.outputs[output_key]

if current_output:
    st.code(current_output, language="markdown")

    # ---------------- ELITE FEATURE: REFINE ----------------
    st.markdown("### Refine Output")
    refine_text = st.text_input("Ask AI to refine this (e.g., Make concise, Convert to OKRs)")

    if st.button("Refine"):
        refined = generate(output_key, refine_text)
        st.session_state.outputs[output_key]=refined

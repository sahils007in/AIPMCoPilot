import streamlit as st
from openai import OpenAI
import time
import hashlib

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI PM Copilot", page_icon="🚀", layout="wide")

st.title("🚀 AI Product Manager Copilot")
st.caption("AI Workspace for Product Managers — Intelligent Artifact Generation")

# ---------------- SESSION STATE ----------------
defaults = {
    "client": None,
    "api_key_valid": False,
    "validated_key": None,
    "outputs": {"summary":"","actions":"","prd":"","stories":""},
    "active_view": "Executive Summary",
    "suggestions": [],
    "suggestion_explanations": {},
    "memory": [],
    "workflow_cache_key": None,
    "workflow_advice": ""
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
    st.header("⚙ Configuration")

    api_key = st.text_input("OpenAI API Key", type="password")

    role = st.selectbox("PM Role",["Startup PM","Agile Coach","Technical PM"])
    tone = st.selectbox("Output Style",["Concise","Detailed"])

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

if not st.session_state.api_key_valid:
    st.info("Enter valid OpenAI API key to continue.")
    st.stop()

client = st.session_state.client

# ---------------- INPUT ----------------
user_input = st.text_area("Paste meeting notes or product ideas", height=220)
input_empty = not user_input.strip()

# ---------------- MEMORY ----------------
def get_memory_context():
    if not st.session_state.memory:
        return ""
    return "\n\nPrevious Artifacts:\n" + "\n\n".join(st.session_state.memory)

def add_to_memory(content):
    if content and content not in st.session_state.memory:
        st.session_state.memory.append(content)

# ---------------- PROMPT BUILDER ----------------
def build_prompt(task, refine=None, existing=None):

    if refine and existing:
        return f"""
Refine this output:

{existing}

Request:
{refine}
"""

    base = f"""
You are an expert Product Manager.

PM Style: {role}
Response Style: {tone}

Input:
{user_input}

{get_memory_context()}
"""

    tasks = {
        "summary":"Create executive summary.",
        "actions":"Extract prioritized action items.",
        "prd":"Create structured PRD (Problem, Users, Goals, Metrics, Features, Risks).",
        "stories":"Generate Agile user stories with acceptance criteria."
    }

    return base + "\nTask:\n" + tasks[task]

# ---------------- WORKFLOW COACH ----------------
def get_workflow_advice():

    state_hash = hashlib.md5(str(st.session_state.outputs).encode()).hexdigest()

    if state_hash == st.session_state.workflow_cache_key:
        return st.session_state.workflow_advice

    generated = [k for k,v in st.session_state.outputs.items() if v]

    prompt = f"""
You are an AI workflow coach for Product Managers.

Artifacts generated: {generated}

Suggest ONE strategic next step in 1-2 sentences.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3
    )

    advice = response.choices[0].message.content

    st.session_state.workflow_cache_key = state_hash
    st.session_state.workflow_advice = advice

    return advice

# ---------------- AI SUGGESTIONS ----------------
def get_ai_suggestions(current_output):

    prompt = f"""
Suggest EXACTLY 3 useful next refinement actions.
Return format:
Action | Reason

{current_output}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3
    )

    raw = response.choices[0].message.content

    suggestions = []
    explanations = {}

    for line in raw.split("\n"):

        # ✅ FIX: remove header row "Action | Reason"
        if "Action" in line and "Reason" in line:
            continue

        if "|" not in line:
            continue

        action, reason = line.split("|",1)

        action = action.replace("Action:", "").replace("-", "").replace("•","").strip()
        reason = reason.replace("Reason:", "").strip()

        if len(action) < 3:
            continue

        suggestions.append(action)
        explanations[action] = reason

    suggestions = list(dict.fromkeys(suggestions))

    st.session_state.suggestions = suggestions[:3]
    st.session_state.suggestion_explanations = explanations

# ---------------- GENERATE ----------------
def generate(task, refine=None):

    existing = st.session_state.outputs[task] if refine else None
    prompt = build_prompt(task, refine, existing)

    start = time.time()

    with st.spinner("Generating..."):
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )

    duration = round(time.time() - start, 2)
    st.success(f"Generated in {duration}s")

    result = res.choices[0].message.content

    add_to_memory(result)
    get_ai_suggestions(result)

    return result

# ---------------- GENERATE BUTTONS ----------------
st.markdown("### Generate Artifacts")

col0,col1,col2,col3,col4 = st.columns(5)

with col0:
    if st.button("🚀 Generate All", disabled=input_empty):
        for key in ["summary","actions","prd","stories"]:
            st.session_state.outputs[key] = generate(key)
        st.session_state.active_view = "Executive Summary"
        st.rerun()

with col1:
    if st.button("Executive Summary", disabled=input_empty):
        st.session_state.outputs["summary"] = generate("summary")
        st.session_state.active_view = "Executive Summary"
        st.rerun()

with col2:
    if st.button("Action Items", disabled=input_empty):
        st.session_state.outputs["actions"] = generate("actions")
        st.session_state.active_view = "Action Items"
        st.rerun()

with col3:
    if st.button("Generate PRD", disabled=input_empty):
        st.session_state.outputs["prd"] = generate("prd")
        st.session_state.active_view = "PRD"
        st.rerun()

with col4:
    if st.button("User Stories", disabled=input_empty):
        st.session_state.outputs["stories"] = generate("stories")
        st.session_state.active_view = "User Stories"
        st.rerun()

# ---------------- WORKSPACE ----------------
st.markdown("---")

views = ["Executive Summary","Action Items","PRD","User Stories"]

selected = st.radio("Workspace", views, horizontal=True,
                    index=views.index(st.session_state.active_view))

output_key = {
    "Executive Summary":"summary",
    "Action Items":"actions",
    "PRD":"prd",
    "User Stories":"stories"
}[selected]

current_output = st.session_state.outputs[output_key]

# ---------------- WORKFLOW COACH DISPLAY ----------------
if any(st.session_state.outputs.values()):
    st.markdown("### 🧠 Workflow Coach")
    st.info(get_workflow_advice())

# ---------------- OUTPUT DISPLAY ----------------
if current_output:

    st.markdown("### Output")
    st.code(current_output)

    st.markdown("### Quick Refine")

    options = ["Make concise","Convert to OKRs","Add risks section","Make technical"]
    cols = st.columns(len(options))

    for i,opt in enumerate(options):
        if cols[i].button(opt):
            st.session_state.outputs[output_key] = generate(output_key,opt)
            st.rerun()

    custom = st.text_input("Custom refine")

    if st.button("Apply Custom Refine"):
        if custom.strip():
            st.session_state.outputs[output_key] = generate(output_key,custom)
            st.rerun()

    if st.session_state.suggestions:
        st.markdown("### 🤖 AI Suggested Next Steps")

        for suggestion in st.session_state.suggestions:
            col1,col2 = st.columns([1,6])

            with col1:
                if st.button(suggestion):
                    st.session_state.outputs[output_key] = generate(output_key,suggestion)
                    st.rerun()

            with col2:
                reason = st.session_state.suggestion_explanations.get(suggestion,"")
                st.caption(f"👉 Why: {reason}")

    st.download_button(
        "⬇ Export Markdown",
        current_output,
        file_name=f"{output_key}.md"
    )

else:
    st.info("Generate an artifact to start building your workspace.")

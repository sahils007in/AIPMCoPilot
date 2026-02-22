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
    "suggestion_confidence": {},
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
        "prd":"Create structured PRD.",
        "stories":"Generate Agile user stories."
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

Suggest ONE strategic next step.
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
Action | Reason | Confidence(High/Medium/Low)

{current_output}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3
    )

    raw = response.choices[0].message.content

    suggestions=[]
    explanations={}
    confidence_scores={}

    for line in raw.split("\n"):

        line=line.strip()

        if not line or "|" not in line:
            continue

        parts=line.split("|")

        if len(parts)<3:
            continue

        action=parts[0].replace("Action:", "").strip()
        reason=parts[1].replace("Reason:", "").strip()
        confidence=parts[2].replace("Confidence:", "").strip()

        if action.lower() in ["action","actions"]:
            continue

        if len(action)<5:
            continue

        suggestions.append(action)
        explanations[action]=reason
        confidence_scores[action]=confidence

    suggestions=list(dict.fromkeys(suggestions))

    st.session_state.suggestions=suggestions[:3]
    st.session_state.suggestion_explanations=explanations
    st.session_state.suggestion_confidence=confidence_scores

# ---------------- GENERATE ----------------
def generate(task, refine=None):

    existing = st.session_state.outputs[task] if refine else None
    prompt = build_prompt(task, refine, existing)

    with st.spinner("Generating..."):
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )

    result = res.choices[0].message.content

    add_to_memory(result)
    get_ai_suggestions(result)

    return result

# ---------------- GENERATE BUTTONS ----------------
st.markdown("### Generate Artifacts")

cols=st.columns(5)

labels=["🚀 Generate All","Executive Summary","Action Items","Generate PRD","User Stories"]
keys=["all","summary","actions","prd","stories"]

for i,label in enumerate(labels):
    if cols[i].button(label, disabled=input_empty):
        if keys[i]=="all":
            for k in ["summary","actions","prd","stories"]:
                st.session_state.outputs[k]=generate(k)
        else:
            st.session_state.outputs[keys[i]]=generate(keys[i])
        st.rerun()

# ---------------- WORKFLOW COACH ----------------
if any(st.session_state.outputs.values()):
    st.markdown("### 🧠 Workflow Coach")
    st.info(get_workflow_advice())

# ---------------- DISPLAY OUTPUT ----------------
for key,val in st.session_state.outputs.items():
    if val:
        st.code(val)

# ---------------- SUGGESTIONS DISPLAY ----------------
if st.session_state.suggestions:

    st.markdown("### 🤖 AI Suggested Next Steps")

    for suggestion in st.session_state.suggestions:

        conf=st.session_state.suggestion_confidence.get(suggestion,"")
        reason=st.session_state.suggestion_explanations.get(suggestion,"")

        if st.button(f"{suggestion} ⭐ {conf}"):
            st.session_state.outputs["summary"]=generate("summary",suggestion)
            st.rerun()

        st.caption(f"👉 Why: {reason}")

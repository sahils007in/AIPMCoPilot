import streamlit as st
from openai import OpenAI
import hashlib

# ---------------- PAGE ----------------
st.set_page_config(page_title="AI PM Copilot", page_icon="🚀", layout="wide")

st.title("🚀 AI Product Manager Copilot")
st.caption("AI Workspace for Product Managers")

# ---------------- SESSION STATE ----------------
defaults = {
    "client": None,
    "api_key_valid": False,
    "validated_key": None,
    "outputs": {"summary":"","actions":"","prd":"","stories":""},
    "memory": [],
    "timeline": [],
    "suggestions": [],
    "suggestion_explanations": {},
    "suggestion_confidence": {},
    "workflow_cache_key": None,
    "workflow_advice": "",
    "product_stage": "Unknown"
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
    st.stop()

client = st.session_state.client

# ---------------- INPUT ----------------
user_input = st.text_area("Paste meeting notes or product ideas", height=200)

# ---------------- MEMORY ----------------
def get_memory_context():
    return "\n".join(st.session_state.memory)

def add_memory(text):
    if text and text not in st.session_state.memory:
        st.session_state.memory.append(text)

def add_timeline(event):
    st.session_state.timeline.append(event)

# ---------------- PRODUCT STAGE INTELLIGENCE ----------------
def detect_product_stage():

    combined = user_input + " ".join(st.session_state.memory)

    prompt=f"""
Determine product stage:

Discovery = research/validation
Delivery = execution/PRD
Growth = metrics/optimization

Return ONE word only.
Text:
{combined}
"""

    res=client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    stage=res.choices[0].message.content.strip()

    if stage not in ["Discovery","Delivery","Growth"]:
        stage="Discovery"

    st.session_state.product_stage=stage

# ---------------- PROMPT BUILDER ----------------
def build_prompt(task, refine=None, existing=None):

    if refine and existing:
        return f"Refine:\n{existing}\nRequest:{refine}"

    base=f"""
You are expert Product Manager.

Detected Product Stage: {st.session_state.product_stage}

Role:{role}
Tone:{tone}

Input:
{user_input}

Previous Context:
{get_memory_context()}
"""

    tasks={
        "summary":"Create executive summary.",
        "actions":"Extract action items.",
        "prd":"Create structured PRD.",
        "stories":"Generate user stories."
    }

    return base + tasks[task]

# ---------------- WORKFLOW COACH ----------------
def workflow_coach():

    state_hash=hashlib.md5(str(st.session_state.outputs).encode()).hexdigest()

    if state_hash==st.session_state.workflow_cache_key:
        return st.session_state.workflow_advice

    generated=[k for k,v in st.session_state.outputs.items() if v]

    prompt=f"Artifacts:{generated}. Suggest next best PM step."

    res=client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    advice=res.choices[0].message.content

    st.session_state.workflow_cache_key=state_hash
    st.session_state.workflow_advice=advice

    return advice

# ---------------- AI SUGGESTIONS ----------------
def get_ai_suggestions(output):

    prompt=f"""
Suggest 3 next actions.

Format:
Action | Reason | Confidence

{output}
"""

    res=client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    suggestions=[]
    reasons={}
    conf={}

    for line in res.choices[0].message.content.split("\n"):

        if "|" not in line:
            continue

        parts=line.split("|")

        if len(parts)<3:
            continue

        action=parts[0].strip()

        if action.lower()=="action":
            continue

        suggestions.append(action)
        reasons[action]=parts[1].strip()
        conf[action]=parts[2].strip()

    st.session_state.suggestions=suggestions[:3]
    st.session_state.suggestion_explanations=reasons
    st.session_state.suggestion_confidence=conf

# ---------------- GENERATE ----------------
def generate(task, refine=None):

    existing=st.session_state.outputs[task] if refine else None
    prompt=build_prompt(task,refine,existing)

    with st.spinner("Generating..."):
        res=client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )

    result=res.choices[0].message.content

    st.session_state.outputs[task]=result

    add_memory(result)
    add_timeline(f"{task.upper()} updated")
    detect_product_stage()
    get_ai_suggestions(result)

# ---------------- BUTTONS ----------------
cols=st.columns(4)

if cols[0].button("Executive Summary"):
    generate("summary")

if cols[1].button("Action Items"):
    generate("actions")

if cols[2].button("Generate PRD"):
    generate("prd")

if cols[3].button("User Stories"):
    generate("stories")

# ---------------- STAGE BADGE ----------------
if st.session_state.product_stage!="Unknown":
    st.markdown(f"### 🧭 Product Stage Detected: **{st.session_state.product_stage}**")

# ---------------- WORKFLOW COACH ----------------
if any(st.session_state.outputs.values()):
    st.markdown("### 🧠 Workflow Coach")
    st.info(workflow_coach())

# ---------------- OUTPUT ----------------
current_output=None
for v in st.session_state.outputs.values():
    if v:
        current_output=v

if current_output:

    st.code(current_output)

    st.markdown("### Quick Refine")

    opts=["Make concise","Convert to OKRs","Add risks section","Make technical"]
    cols=st.columns(len(opts))

    for i,opt in enumerate(opts):
        if cols[i].button(opt):
            generate("summary",opt)

    custom=st.text_input("Custom refine")

    if st.button("Apply Custom Refine"):
        generate("summary",custom)

    st.markdown("### 🤖 AI Suggested Next Steps")

    for s in st.session_state.suggestions:

        conf=st.session_state.suggestion_confidence.get(s,"")
        reason=st.session_state.suggestion_explanations.get(s,"")

        if st.button(f"{s} ⭐ {conf}"):
            generate("summary",s)

        st.caption(f"👉 Why: {reason}")

# ---------------- TIMELINE ----------------
if st.session_state.timeline:

    st.markdown("### 📜 AI Workflow Timeline")

    for step in st.session_state.timeline[::-1]:
        st.write(f"✅ {step}")

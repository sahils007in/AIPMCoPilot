import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Product Manager Copilot", page_icon="🚀")

# =========================
# SESSION STATE
# =========================
if "api_valid" not in st.session_state:
    st.session_state.api_valid=False

if "active_tab" not in st.session_state:
    st.session_state.active_tab="Executive Summary"

if "artifacts" not in st.session_state:
    st.session_state.artifacts={
        "Executive Summary":"",
        "Action Items":"",
        "PRD":"",
        "User Stories":""
    }

if "suggestions" not in st.session_state:
    st.session_state.suggestions=[]

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key=st.text_input("OpenAI API Key",type="password")
    pm_role=st.selectbox("PM Role",["Startup PM","Growth PM","Enterprise PM"])
    output_style=st.selectbox("Output Style",["Concise","Detailed"])

    st.markdown("---")
    st.markdown("Built by Sahil Jain 🚀  \n[LinkedIn](https://linkedin.com)")

# =========================
# HEADER
# =========================
st.title("🚀 AI Product Manager Copilot")
st.caption("AI Workspace for Product Managers")

# =========================
# API VALIDATION
# =========================
def validate_key(key):
    try:
        OpenAI(api_key=key).models.list()
        return True
    except:
        return False

if api_key and not st.session_state.api_valid:
    with st.spinner("Validating API Key..."):
        st.session_state.api_valid=validate_key(api_key)

if not api_key:
    st.warning("🔑 Enter your OpenAI API key in sidebar.")
    st.stop()

if not st.session_state.api_valid:
    st.error("❌ Invalid API key")
    st.stop()

st.success("🟢 Connected to OpenAI")
client=OpenAI(api_key=api_key)

# =========================
# INPUT
# =========================
product_input=st.text_area(
"📥 Paste Product Context (Idea, Notes, Transcript, or Any Raw Input)",
height=200
)

# =========================
# AI CALL
# =========================
def ask_ai(prompt):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    ).choices[0].message.content

# =========================
# GENERATION
# =========================
def generate(type_name):

    with st.spinner(f"Generating {type_name}..."):

        result=ask_ai(f"""
Act as senior product manager.

Generate {type_name}.

Role:{pm_role}
Style:{output_style}

Context:
{product_input}
""")

        st.session_state.artifacts[type_name]=result
        st.session_state.active_tab=type_name

        # generate suggestions
        suggestion_text=ask_ai(f"""
Suggest 3 next PM actions with confidence (High/Medium/Low) and short reason.

Context:
{product_input}
""")

        st.session_state.suggestions=suggestion_text.split("\n")

def generate_all():
    for k in st.session_state.artifacts.keys():
        generate(k)

# =========================
# BUTTON ROW
# =========================
col1,col2,col3,col4,col5=st.columns(5)

with col1:
    if st.button("🚀 Generate All"):
        generate_all()

with col2:
    if st.button("Executive Summary"):
        generate("Executive Summary")

with col3:
    if st.button("Action Items"):
        generate("Action Items")

with col4:
    if st.button("PRD"):
        generate("PRD")

with col5:
    if st.button("User Stories"):
        generate("User Stories")

# =========================
# OUTPUT TABS
# =========================
if any(st.session_state.artifacts.values()):

    st.markdown("---")

    tabs=st.tabs(list(st.session_state.artifacts.keys()))

    for i,key in enumerate(st.session_state.artifacts.keys()):
        with tabs[i]:
            if key==st.session_state.active_tab:
                st.markdown(st.session_state.artifacts[key])

# =========================
# QUICK REFINE
# =========================
if st.session_state.artifacts[st.session_state.active_tab]:

    st.subheader("Quick Refine")

    r1,r2,r3,r4=st.columns(4)

    if r1.button("Make concise"):
        st.session_state.artifacts[st.session_state.active_tab]=ask_ai(
            "Make concise:\n"+st.session_state.artifacts[st.session_state.active_tab])

    if r2.button("Convert to OKRs"):
        st.session_state.artifacts[st.session_state.active_tab]=ask_ai(
            "Convert to OKRs:\n"+st.session_state.artifacts[st.session_state.active_tab])

    if r3.button("Add risks"):
        st.session_state.artifacts[st.session_state.active_tab]=ask_ai(
            "Add risks section:\n"+st.session_state.artifacts[st.session_state.active_tab])

    if r4.button("Make technical"):
        st.session_state.artifacts[st.session_state.active_tab]=ask_ai(
            "Make technical:\n"+st.session_state.artifacts[st.session_state.active_tab])

# =========================
# AI SUGGESTIONS
# =========================
if st.session_state.suggestions:

    st.markdown("---")
    st.subheader("🤖 AI Suggested Next Steps")

    for s in st.session_state.suggestions:

        if not s.strip():
            continue

        confidence="⭐ Medium"
        if "High" in s: confidence="⭐ High"
        elif "Low" in s: confidence="⭐ Low"

        clean=s.replace("High","").replace("Medium","").replace("Low","")

        st.markdown(f"**{clean}** {confidence}")

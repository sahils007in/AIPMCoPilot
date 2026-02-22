import streamlit as st
from openai import OpenAI

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Product Manager Copilot", page_icon="🚀")

# =========================
# SESSION STATE
# =========================
if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False
if "memory_output" not in st.session_state:
    st.session_state.memory_output = ""
if "ai_suggestions" not in st.session_state:
    st.session_state.ai_suggestions = []

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.title("⚙️ Configuration")

    api_key = st.text_input("OpenAI API Key", type="password")

    pm_role = st.selectbox("PM Role", ["Startup PM","Growth PM","Enterprise PM"])
    output_style = st.selectbox("Output Style", ["Concise","Detailed"])

    st.markdown("---")
    st.markdown("Built by Sahil Jain 🚀  \n[LinkedIn](https://linkedin.com)")

# =========================
# API KEY VALIDATION
# =========================

def validate_key(key):
    try:
        client = OpenAI(api_key=key)
        client.models.list()
        return True
    except:
        return False

if api_key and not st.session_state.api_key_valid:
    with st.spinner("Validating API Key..."):
        st.session_state.api_key_valid = validate_key(api_key)

# UX messages
if not api_key:
    st.warning("🔑 Enter your OpenAI API key in sidebar to begin.")
    st.stop()

if not st.session_state.api_key_valid:
    st.error("❌ Invalid API key.")
    st.stop()

st.success("🟢 Connected to OpenAI")

client = OpenAI(api_key=api_key)

# =========================
# MAIN HEADER
# =========================
st.title("🚀 AI Product Manager Copilot")
st.caption("AI Workspace for Product Managers")

# =========================
# INPUT
# =========================
idea = st.text_area("Enter Product Idea")

# =========================
# AI GENERATION
# =========================
def ask_ai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return response.choices[0].message.content

# =========================
# GENERATE ALL
# =========================
if st.button("🚀 Generate Artifacts"):

    output = ask_ai(f"""
    Act as Senior Product Manager.

    Generate:
    - PRD
    - User Stories
    - OKRs
    - Risks
    - Metrics

    Idea: {idea}
    Role: {pm_role}
    Style: {output_style}
    """)

    st.session_state.memory_output = output

    suggestions = ask_ai(f"""
    Suggest next PM actions with confidence level (High/Medium/Low)
    and short explanation why.

    Idea: {idea}
    """)

    st.session_state.ai_suggestions = suggestions.split("\n")

# =========================
# DISPLAY OUTPUT
# =========================
if st.session_state.memory_output:
    st.markdown(st.session_state.memory_output)

# =========================
# QUICK REFINE
# =========================
if st.session_state.memory_output:

    st.subheader("Quick Refine")

    col1,col2,col3,col4 = st.columns(4)

    if col1.button("Make concise"):
        st.session_state.memory_output = ask_ai(
            "Make concise:\n"+st.session_state.memory_output)

    if col2.button("Convert to OKRs"):
        st.session_state.memory_output = ask_ai(
            "Convert to OKRs:\n"+st.session_state.memory_output)

    if col3.button("Add risks"):
        st.session_state.memory_output = ask_ai(
            "Add risks section:\n"+st.session_state.memory_output)

    if col4.button("Make technical"):
        st.session_state.memory_output = ask_ai(
            "Make technical:\n"+st.session_state.memory_output)

    custom_refine = st.text_input("Custom refine")

    if st.button("Apply Custom Refine"):
        if custom_refine:
            st.session_state.memory_output = ask_ai(
                custom_refine+"\n"+st.session_state.memory_output)

# =========================
# AI NEXT STEPS
# =========================
if st.session_state.ai_suggestions:

    st.subheader("🤖 AI Suggested Next Steps")

    for s in st.session_state.ai_suggestions:

        if not s.strip():
            continue

        confidence = "⭐ Medium"
        if "High" in s:
            confidence = "⭐ High"
        elif "Low" in s:
            confidence = "⭐ Low"

        st.markdown(f"**{s.replace('High','').replace('Medium','').replace('Low','')}** {confidence}")

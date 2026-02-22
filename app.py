import streamlit as st
from openai import OpenAI

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Product Manager Copilot", page_icon="🚀")

# =========================
# SESSION STATE
# =========================
if "api_valid" not in st.session_state:
    st.session_state.api_valid = False
if "output" not in st.session_state:
    st.session_state.output = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

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
# HEADER (ALWAYS VISIBLE)
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
        st.session_state.api_valid = validate_key(api_key)

if not api_key:
    st.warning("🔑 Enter your OpenAI API key in sidebar to begin.")
    st.stop()

if not st.session_state.api_valid:
    st.error("❌ Invalid API Key")
    st.stop()

st.success("🟢 Connected to OpenAI")

client = OpenAI(api_key=api_key)

# =========================
# INPUT
# =========================
product_input = st.text_area(
    "📥 Paste Product Context (Idea, Notes, Transcript, or Any Raw Input)",
    height=200
)

st.caption("Supports ideas, meeting notes, transcripts, research inputs or unstructured text.")

# =========================
# AI CALL
# =========================
def ask_ai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return response.choices[0].message.content

# =========================
# ARTIFACT GENERATION
# =========================
def generate_artifact(type_name):
    prompt = f"""
Act as Senior Product Manager.

Generate {type_name} for the following context.

Role: {pm_role}
Style: {output_style}

Context:
{product_input}
"""
    result = ask_ai(prompt)
    st.session_state.output = result

    suggestion_text = ask_ai(f"""
Suggest next PM actions with confidence (High/Medium/Low) and short reason.

Context:
{product_input}
""")

    st.session_state.suggestions = suggestion_text.split("\n")

# =========================
# BUTTONS ROW
# =========================
col1, col2, col3, col4, col5 = st.columns(5)

if col1.button("Executive Summary"):
    generate_artifact("Executive Summary")

if col2.button("Action Items"):
    generate_artifact("Action Items")

if col3.button("PRD"):
    generate_artifact("Product Requirements Document")

if col4.button("User Stories"):
    generate_artifact("User Stories")

if col5.button("🚀 Generate All"):
    generate_artifact("Executive Summary, PRD, User Stories, OKRs, Risks and Metrics")

# =========================
# DISPLAY OUTPUT
# =========================
if st.session_state.output:
    st.markdown("---")
    st.markdown(st.session_state.output)

# =========================
# QUICK REFINE
# =========================
if st.session_state.output:

    st.subheader("Quick Refine")

    r1, r2, r3, r4 = st.columns(4)

    if r1.button("Make concise"):
        st.session_state.output = ask_ai(
            "Make concise:\n"+st.session_state.output)

    if r2.button("Convert to OKRs"):
        st.session_state.output = ask_ai(
            "Convert to OKRs:\n"+st.session_state.output)

    if r3.button("Add risks"):
        st.session_state.output = ask_ai(
            "Add risks section:\n"+st.session_state.output)

    if r4.button("Make technical"):
        st.session_state.output = ask_ai(
            "Make technical:\n"+st.session_state.output)

    custom_refine = st.text_input("Custom refine")

    if st.button("Apply Custom Refine"):
        if custom_refine:
            st.session_state.output = ask_ai(
                custom_refine+"\n"+st.session_state.output)

# =========================
# AI SUGGESTED NEXT STEPS
# =========================
if st.session_state.suggestions:

    st.markdown("---")
    st.subheader("🤖 AI Suggested Next Steps")

    for s in st.session_state.suggestions:
        if not s.strip():
            continue

        confidence = "⭐ Medium"
        if "High" in s:
            confidence = "⭐ High"
        elif "Low" in s:
            confidence = "⭐ Low"

        clean = s.replace("High","").replace("Medium","").replace("Low","")

        st.markdown(f"**{clean}** {confidence}")

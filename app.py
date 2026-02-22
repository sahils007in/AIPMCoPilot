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

if "artifacts" not in st.session_state:
    st.session_state.artifacts = {
        "Executive Summary": "",
        "Action Items": "",
        "PRD": "",
        "User Stories": ""
    }

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
# GENERATION FUNCTIONS
# =========================
def generate_single(type_name):
    prompt = f"""
Act as Senior Product Manager.

Generate {type_name}.

Role: {pm_role}
Style: {output_style}

Context:
{product_input}
"""
    return ask_ai(prompt)


def generate_all():
    st.session_state.artifacts["Executive Summary"] = generate_single("Executive Summary")
    st.session_state.artifacts["Action Items"] = generate_single("Action Items")
    st.session_state.artifacts["PRD"] = generate_single("Product Requirements Document")
    st.session_state.artifacts["User Stories"] = generate_single("User Stories")

    suggestion_text = ask_ai(f"""
Suggest 3 next PM steps with confidence level (High/Medium/Low)
and short explanation.

Context:
{product_input}
""")

    st.session_state.suggestions = suggestion_text.split("\n")

# =========================
# BUTTON ROW (EQUAL SPACING)
# =========================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🚀 Generate All"):
        generate_all()

with col2:
    if st.button("Executive Summary"):
        st.session_state.artifacts["Executive Summary"] = generate_single("Executive Summary")

with col3:
    if st.button("Action Items"):
        st.session_state.artifacts["Action Items"] = generate_single("Action Items")

with col4:
    if st.button("PRD"):
        st.session_state.artifacts["PRD"] = generate_single("Product Requirements Document")

with col5:
    if st.button("User Stories"):
        st.session_state.artifacts["User Stories"] = generate_single("User Stories")

# =========================
# OUTPUT TABS
# =========================
if any(st.session_state.artifacts.values()):

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Executive Summary","Action Items","PRD","User Stories"]
    )

    with tab1:
        st.markdown(st.session_state.artifacts["Executive Summary"])

    with tab2:
        st.markdown(st.session_state.artifacts["Action Items"])

    with tab3:
        st.markdown(st.session_state.artifacts["PRD"])

    with tab4:
        st.markdown(st.session_state.artifacts["User Stories"])

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

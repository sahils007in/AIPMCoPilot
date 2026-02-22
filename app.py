import streamlit as st
from openai import OpenAI
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI PM Copilot", page_icon="🚀", layout="wide")

st.title("🚀 AI Product Manager Copilot")
st.caption("AI Workspace for Product Managers — turn messy thinking into structured artifacts.")

# ---------------- SESSION STATE ----------------
defaults = {
    "client": None,
    "api_key_valid": False,
    "validated_key": None,
    "outputs": {
        "summary": "",
        "actions": "",
        "prd": "",
        "stories": ""
    },
    "active_view": "Executive Summary"
}

for k, v in defaults.items():
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

# Block usage until valid API key
if not st.session_state.api_key_valid:
    st.info("Enter a valid OpenAI API key to continue.")
    st.stop()

client = st.session_state.client

# ---------------- INPUT ----------------
user_input = st.text_area(
    "Paste meeting notes, product ideas, or transcripts",
    height=220
)

input_empty = not user_input.strip()

# ---------------- PROMPT BUILDER ----------------
def build_prompt(task, refine=None, existing=None):

    if refine and existing:
        return f"""
You are an expert Product Manager.

Refine the following output.

Current Output:
{existing}

Refinement Request:
{refine}
"""

    base = f"""
You are an expert Product Manager.

PM Style: {role}
Response Style: {tone}

Input:
{user_input}
"""

    tasks = {
        "summary": "Create executive summary.",
        "actions": "Extract prioritized action items.",
        "prd": "Create structured PRD (Problem, Users, Goals, Metrics, Features, Risks).",
        "stories": "Generate Agile user stories with acceptance criteria."
    }

    return base + "\nTask:\n" + tasks[task]

# ---------------- GENERATE FUNCTION ----------------
def generate(task, refine=None):

    start = time.time()

    existing = st.session_state.outputs[task] if refine else None

    prompt = build_prompt(task, refine, existing)

    with st.spinner("Generating..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

    duration = round(time.time() - start, 2)
    st.success(f"Generated in {duration}s")

    return response.choices[0].message.content

# ---------------- BUTTON SECTION ----------------
st.markdown("### Generate Artifacts")

col0, col1, col2, col3, col4 = st.columns(5)

# Generate All
with col0:
    if st.button("🚀 Generate All", disabled=input_empty):
        with st.spinner("Generating all artifacts..."):
            st.session_state.outputs["summary"] = generate("summary")
            st.session_state.outputs["actions"] = generate("actions")
            st.session_state.outputs["prd"] = generate("prd")
            st.session_state.outputs["stories"] = generate("stories")

        st.session_state.active_view = "Executive Summary"
        st.rerun()

# Individual Buttons
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

# ---------------- ARTIFACT STATUS ----------------
st.markdown("### Artifact Status")

status_cols = st.columns(4)
labels = ["summary", "actions", "prd", "stories"]
names = ["Executive Summary", "Action Items", "PRD", "User Stories"]

for i in range(4):
    status = "✅" if st.session_state.outputs[labels[i]] else "⏳"
    status_cols[i].metric(names[i], status)

# ---------------- WORKSPACE VIEW ----------------
st.markdown("---")

views = ["Executive Summary", "Action Items", "PRD", "User Stories"]

selected = st.radio(
    "Workspace",
    views,
    horizontal=True,
    index=views.index(st.session_state.active_view)
)

output_key = {
    "Executive Summary": "summary",
    "Action Items": "actions",
    "PRD": "prd",
    "User Stories": "stories"
}[selected]

current_output = st.session_state.outputs[output_key]

if current_output:

    st.code(current_output, language="markdown")

    # ---------------- QUICK REFINE ----------------
    st.markdown("### Quick Refine")

    refine_options = [
        "Make concise",
        "Convert to OKRs",
        "Add risks section",
        "Make more technical"
    ]

    refine_cols = st.columns(len(refine_options))

    for i, opt in enumerate(refine_options):
        if refine_cols[i].button(opt):
            new_output = generate(output_key, opt)
            st.session_state.outputs[output_key] = new_output
            st.rerun()

    # -------- CUSTOM REFINE INPUT --------
    st.markdown("#### Or enter custom refinement")

    custom_col1, custom_col2 = st.columns([4,1])

    with custom_col1:
        custom_refine = st.text_input(
            "Custom refine request",
            placeholder="e.g., Convert to OKRs, Add roadmap, Simplify language"
        )

    with custom_col2:
        if st.button("Apply"):
            if custom_refine.strip():
                new_output = generate(output_key, custom_refine)
                st.session_state.outputs[output_key] = new_output
                st.rerun()

    # ---------------- EXPORT ----------------
    st.download_button(
        "⬇ Export Markdown",
        current_output,
        file_name=f"{output_key}.md",
        mime="text/markdown"
    )

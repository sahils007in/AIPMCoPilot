# ---------------- ACTION BUTTONS ----------------

st.markdown("### Generate Artifacts")

col0, col1, col2, col3, col4 = st.columns(5)

# ---- GENERATE ALL ----
with col0:
    if st.button("🚀 Generate All", disabled=input_empty):

        with st.spinner("Generating all artifacts..."):

            st.session_state.outputs["summary"] = generate("summary")
            st.session_state.outputs["actions"] = generate("actions")
            st.session_state.outputs["prd"] = generate("prd")
            st.session_state.outputs["stories"] = generate("stories")

        st.session_state.active_view = "Executive Summary"
        st.rerun()

# ---- INDIVIDUAL BUTTONS ----
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

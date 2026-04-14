# ============================================================
# JIRA Ticket Writer — Streamlit App
# Converts raw notes into structured JIRA tickets using Claude
# ============================================================

import anthropic
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (local dev only)
# In production (Streamlit Cloud), secrets are set in the dashboard
load_dotenv()

# Initialize the Anthropic client using the API key from environment
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Page config ──────────────────────────────────────────────
# Sets the browser tab title and favicon
st.set_page_config(page_title="JIRA Ticket Writer", page_icon="🎫")

# ── Header ───────────────────────────────────────────────────
st.title("🎫 JIRA Ticket Writer")
st.subheader("Stop wasting time formatting JIRA tickets. Paste your raw notes and get a ready-to-copy ticket in 10 seconds.")

# ── Input ────────────────────────────────────────────────────
# Multi-line text box where the user pastes their raw notes
raw_notes = st.text_area(
    "Paste your raw notes here",
    placeholder="e.g. Met with design team. Need to update dashboard filters. Users want to filter by assignee and status. Sarah's team is blocked on weekly reviews. Needs to work on mobile.",
    height=200
)

# ── Generate button ──────────────────────────────────────────
# Nothing happens until the user clicks this
if st.button("Generate Ticket", type="primary"):
    
    # Guard clause — don't call the API if the input is empty
    if not raw_notes.strip():
        st.warning("Please paste some notes first.")
    else:
        # Show a spinner while the API call is in flight
        with st.spinner("Writing your ticket..."):
            
            # ── Prompt ───────────────────────────────────────
            # This is the core of the product.
            # V1 SCOPE: Summary, Description, Acceptance Criteria, Priority
            # INTENTIONALLY EXCLUDED: Story Points (team-dependent, not AI's call)
            # OUT OF SCOPE: Epic, Labels, Sprint, Reporter, Custom fields
            prompt = f"""You are a JIRA ticket writer for product teams.
Convert the following raw notes into a structured JIRA ticket.

Raw notes:
{raw_notes}

Return the ticket in exactly this format:

**Summary:** [One line, action-oriented, under 10 words]

**Description:**
[2-3 sentences of context. What is this and why does it matter?]

**Acceptance Criteria:**
- [ ] [Testable condition 1]
- [ ] [Testable condition 2]
- [ ] [Testable condition 3]

**Priority:** [Critical / High / Medium / Low]
"""
            # ── API call ──────────────────────────────────────
            # Sends the prompt to Claude and waits for a response
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the text content from the response object
            result = message.content[0].text
            
            # ── Output ────────────────────────────────────────
            # Render the ticket as formatted markdown
            st.markdown("---")
            st.markdown("### Your JIRA Ticket")
            st.markdown(result)
            
            # Download button — lets users save the ticket as a .txt file
            st.download_button(
                label="Copy as text",
                data=result,
                file_name="jira-ticket.txt",
                mime="text/plain"
            )
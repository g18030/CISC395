import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from src.ai_assistant import ask, TRAVEL_SYSTEM_PROMPT, client
from src.storage import load_trips


st.set_page_config(page_title="Trip Notes AI", page_icon="✈️", layout="wide")


if "trips" not in st.session_state:
    st.session_state.trips = load_trips()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []


trips = st.session_state.trips.get_all()
trip_options = [trip.name for trip in trips] if trips else ["(no trips yet)"]
st.sidebar.title("✈️ Trip Notes AI")
st.sidebar.caption("Powered by Atlas, your travel AI")

selected_trip_name = st.sidebar.selectbox("📍 Current trip", trip_options)
selected_trip = next((trip for trip in trips if trip.name == selected_trip_name), None)

if selected_trip is not None and selected_trip.notes:
    with st.sidebar.expander(f"📋 Notes ({len(selected_trip.notes)})", expanded=False):
        for note in selected_trip.notes:
            st.markdown(f"- {note}")
else:
    st.sidebar.caption("No notes yet for this trip.")

if st.sidebar.button("Generate Briefing"):
    if selected_trip is None or not selected_trip.notes:
        st.sidebar.warning("Add some notes first.")
    else:
        notes_text = "\n".join(f"- {note}" for note in selected_trip.notes)
        briefing_prompt = (
            f"Write a concise travel briefing for {selected_trip.name}, {selected_trip.country}. "
            f"Use these notes as the primary source:\n{notes_text}\n\n"
            "Return a helpful markdown briefing with practical advice."
        )
        briefing = ask(briefing_prompt, system_prompt=TRAVEL_SYSTEM_PROMPT)
        if briefing is None:
            st.sidebar.warning("Briefing unavailable right now.")
        else:
            st.sidebar.markdown(briefing)


chat_tab, search_tab, agent_tab = st.tabs(["💬 Chat", "🔍 Search", "🤖 Agent"])

with chat_tab:
    st.info("Coming soon — Exercise 2")

with search_tab:
    st.info("Coming soon — Exercise 3")

with agent_tab:
    st.info("Coming soon — Exercise 4")
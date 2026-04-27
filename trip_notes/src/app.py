import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from src.ai_assistant import ask, TRAVEL_SYSTEM_PROMPT, MODEL, client
from src.storage import load_trips
from src.ai_assistant import rag_ask
from src.rag import ensure_index


st.set_page_config(page_title="Trip Notes AI", page_icon="✈️", layout="wide")


if "trips" not in st.session_state:
    st.session_state.trips = load_trips()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []


ensure_index()


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
    MAX_TURNS = 8

    st.subheader("Atlas — Your Travel AI")
    st.caption("Ask me anything about travel.")

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask Atlas anything...")
    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        trimmed_history = st.session_state["chat_history"][-(MAX_TURNS * 2):]
        messages = [{"role": "system", "content": TRAVEL_SYSTEM_PROMPT}] + trimmed_history

        with st.spinner("Atlas is thinking..."):
            response = client.chat.completions.create(model=MODEL, messages=messages).choices[0].message.content

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state["chat_history"].append({"role": "assistant", "content": response})

    if st.button("Clear chat", key="clear_chat"):
        st.session_state["chat_history"].clear()
        st.rerun()

with search_tab:
    st.subheader("Search My Guides")
    st.caption("Answers grounded in your guides/ documents.")

    for message in st.session_state["search_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Search your guides...", key="search_input")
    if user_input:
        st.session_state["search_history"].append({"role": "user", "content": user_input})

        with st.spinner("Searching guides..."):
            response = rag_ask(user_input)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state["search_history"].append({"role": "assistant", "content": response})

    if st.button("Clear search", key="clear_search"):
        st.session_state["search_history"].clear()
        st.rerun()

with agent_tab:
    st.info("Coming soon — Exercise 4")
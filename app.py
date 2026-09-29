import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Agentic Workbench",
    page_icon="A",
    layout="centered",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: #18332f;
        --muted: #647873;
        --green: #176b58;
        --green-soft: #e3f0e9;
        --line: #dce6df;
        --coral: #bd5a47;
    }

    .stApp {
        background-color: #f7faf7;
        background-image: repeating-linear-gradient(
            0deg, transparent, transparent 39px, rgba(24, 51, 47, 0.025) 40px
        );
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 900px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, [data-testid='stMarkdownContainer'] h1 {
        color: var(--ink);
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: 0;
    }

    .masthead {
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.4rem;
        padding: 0 0 1.5rem;
    }

    .eyebrow {
        color: var(--green);
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0 0 0.65rem;
    }

    .masthead h1 {
        font-size: 2.5rem;
        line-height: 1.08;
        margin: 0;
    }

    .masthead p:last-child {
        color: var(--muted);
        margin: 0.75rem 0 0;
    }

    [data-testid='stChatMessage'] {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem 1.15rem;
    }

    [data-testid='stChatInput'] {
        border-color: #b9cec2;
    }

    [data-testid='stChatInput'] textarea {
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid='stSidebar'] {
        border-right: 1px solid var(--line);
    }

    .status-line {
        color: var(--muted);
        font-size: 0.9rem;
        padding: 0.6rem 0;
    }

    .stButton button {
        border: 1px solid var(--line);
        border-radius: 6px;
        color: var(--ink);
        background: white;
    }

    .stButton button:hover {
        border-color: var(--green);
        color: var(--green);
    }

    @media (max-width: 640px) {
        .block-container { padding-top: 1.6rem; }
        .masthead h1 { font-size: 2rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("### Agentic Workbench")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    st.caption(f"Model: {model_name}")
    if os.getenv("OPENAI_API_KEY"):
        st.success("API key detected")
    else:
        st.warning("Set OPENAI_API_KEY in your .env file to run requests.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown(
    """
    <header class='masthead'>
        <p class='eyebrow'>Reasoning · Tools · Answers</p>
        <h1>Agentic Workbench</h1>
        <p>What would you like to work through?</p>
    </header>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.caption("Try a calculation or ask a general question.")
    suggestion_columns = st.columns(3)
    suggestions = (
        "Square the average of 10 and 5",
        "What is artificial intelligence?",
        "What is 18% of 250?",
    )
    for index, suggestion in enumerate(suggestions):
        if suggestion_columns[index].button(suggestion, key=f"suggestion_{index}", use_container_width=True):
            st.session_state.pending_prompt = suggestion
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("expression"):
            st.caption(f"Calculator expression: `{message['expression']}`")

prompt = st.chat_input("Ask a question or enter a calculation")
if prompt is None:
    prompt = st.session_state.pop("pending_prompt", None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not os.getenv("OPENAI_API_KEY"):
            answer = "Add a valid OPENAI_API_KEY to your .env file, then restart the app."
            st.error(answer)
            expression = None
        else:
            try:
                from patterns.using_tools.graph import build_graph

                with st.spinner("Working through your question..."):
                    result = build_graph().invoke({"question": prompt})
                answer = result["result"]
                expression = result.get("expression") if result.get("intent") == "math" else None
                st.markdown(answer)
                if expression:
                    st.caption(f"Calculator expression: `{expression}`")
            except Exception:
                answer = "I couldn't complete that request. Check your API key, model access, and connection, then try again."
                expression = None
                st.error(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "expression": expression}
    )
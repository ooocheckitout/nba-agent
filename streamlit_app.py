import pandas as pd
import streamlit as st
import sentry_sdk

sentry_sdk.init(
    environment=st.secrets.sentry.environment,
    dsn=st.secrets.sentry.dsn,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    enable_logs=True,
)

import subprocess
import pathlib

index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
logging.info(f"Streamlit index path: {index_path}")

# Streamlit Community Cloud /home/adminuser/venv/lib/site-packages/streamlit/static/index.html
# Streamlit Community Cloud /mount/src/nba-agent
subprocess.run("pwd", shell=True)
subprocess.run("ls /home/adminuser/venv/lib/python3.13", shell=True)
print("----")
subprocess.run("ls /home/adminuser/venv/lib/python3.13/site-packages", shell=True)
print("----")
subprocess.run(
    "ls /home/adminuser/venv/lib/python3.13/site-packages/streamlit/static", shell=True
)
subprocess.run("ls /mount/src/nba-agent", shell=True)
subprocess.run(
    "chmod +x /mount/src/nba-agent/inject-head-stuff.sh && /mount/src/nba-agent/inject-head-stuff.sh",
    shell=True,
)


import time
import logging
from pyisemail import is_email

from models import Message, Suggestion, Role
from typing import Any

st.set_page_config(
    page_title="NBA Stats Agent",
    page_icon="🏀",
    initial_sidebar_state="collapsed",
)
st.title("Nikola Jokic vs Luka Doncic")

messages: list[Message] = [
    Message(
        role=Role.user,
        content="Compare Nikola Jokic vs Luka Doncic in the 2024-25 season.",
    ),
    Message(
        role=Role.assistant,
        content=(
            "In the 2024-25 NBA regular season, Luka Dončić is averaging more points per game, while Nikola Jokić is leading in rebounds and assists per game with significantly higher efficiency.\n\n"
            "### 2024-25 Season Per Game Statistics\n\n"
            "| Statistic | Nikola Jokić (DEN) | Luka Dončić (LAL) |\n"
            "|---|---:|---:|\n"
            "| Points Per Game (PPG) | 29.6 | 28.2 |\n"
            "| Rebounds Per Game (RPG) | 12.7 | 8.1 |\n"
            "| Assists Per Game (APG) | 10.2 | 7.5 |\n"
            "| Steals Per Game (SPG) | 1.8 | 1.6 |\n"
            "| Blocks Per Game (BPG) | 0.6 | 0.4 |\n"
            "| Field Goal Percentage (FG%) | 57.6% | 43.8% |\n"
            "| Three Point Percentage (3P%) | 41.7% | 37.9% |\n\n"
            "### Context and Analysis\n\n"
            "- **Scoring and Efficiency**: Luka Dončić is a slightly higher volume scorer, but Nikola Jokić is significantly more efficient from the field overall, particularly in field goal percentage, and has a better true shooting percentage (TS%).\n"
            "- **Playmaking and Rebounding**: As expected from their positions (Jokić as a center, Dončić as a guard), Jokić has a clear advantage in rebounding, while both are elite passers, with Jokić currently holding a slight edge in assists per game this season.\n"
            "- **Team Performance**: Both players have a significant impact on their respective teams. Jokić's Denver Nuggets had a 1-1 record versus Dončić's Los Angeles Lakers during the games they played against each other in the 2024-25 season.\n"
            "- **Head-to-Head**: In two head-to-head games during the 2024-25 season, Jokić averaged 24.5 points, 15.5 rebounds, and 12.5 assists, while Dončić averaged 28.0 points, 9.5 rebounds, and 8.0 assists.\n\n"
            "*Note: The 2024-25 NBA season concluded in June 2025. The data provided reflects the final statistics for that season.*"
        ),
        columns=["Statistic", "Nikola Jokic", "Luka Doncic"],
        data=[
            ["PPG", 29.6, 28.2],
            ["RPG", 12.7, 8.1],
            ["APG", 10.2, 7.5],
            ["SPG", 1.8, 1.6],
            ["BPG", 0.6, 0.4],
            ["FG%", 57.6, 43.8],
            ["3P%", 41.7, 37.9],
        ],
    ),
]
suggestions: list[Suggestion] = [
    Suggestion(text="📊 Compare their advanced metrics (PER, TS%, WS/48)"),
    Suggestion(text="🔁 Who contributed more in playmaking and clutch moments?"),
    Suggestion(text="🏆 How did each perform in the 2025 playoffs?"),
]
st.markdown(
    """
<style>
    .st-emotion-cache-1fee4w7 {
        flex-direction: row-reverse;
        text-align: right;
    }
</style>
""",
    unsafe_allow_html=True,
)


for message in messages:
    with st.chat_message(message.role):
        st.markdown(message.content)

        if not (message.columns and message.data):
            continue

        st.caption("Visualizations")
        chat_tab, data_tab = st.tabs(["Chart", "Data"])
        with data_tab:
            df = pd.DataFrame(message.data, columns=message.columns)
            # convention first column is x-axis
            df = df.set_index(message.columns[0])
            st.dataframe(df, width="stretch")
        with chat_tab:
            st.bar_chart(df, sort=False, stack=False)


@st.dialog("Get early access", dismissible=False)
def subscribe():
    st.write("Enter your email to get an early access! No spam — unsubscribe anytime.")

    email = st.text_input("Email: ", placeholder="example@gmail.com")

    is_valid_email = is_email(email, check_dns=True)

    if email and not is_valid_email:
        st.warning("Please enter a valid email address.", icon="⚠️")

    if st.button("Register", disabled=not is_valid_email):
        logging.info(f"Registering email: {email}")

        # local_storage.setItem("user", User(email=email).model_dump_json())
        st.success("Thanks — you'll hear from us soon!")

        time.sleep(3)
        st.rerun()


st.caption("Suggestions")
for suggestion in suggestions:
    if st.button(suggestion.text):
        logging.info(f"Suggestion selected: {suggestion.text}")
        subscribe()

st.caption("Knowledge cut-off: June 2025")

if prompt := st.chat_input("Ask me about NBA analytics..."):
    logging.info(f"User prompt: {prompt}")
    subscribe()

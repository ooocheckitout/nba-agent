import pathlib
import subprocess
import pandas as pd
import streamlit as st
import sentry_sdk
import logging
from pyisemail import is_email

from models import DataMessage, Message, Suggestion, Role, TextMessage, User

sentry_sdk.init(
    environment=st.secrets.sentry.environment,
    dsn=st.secrets.sentry.dsn,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    enable_logs=True,
)


@st.cache_data
def make_df(data, columns):
    df = pd.DataFrame(data, columns=columns)
    # convention first column is x-axis
    df = df.set_index(columns[0])
    return df


st.set_page_config(
    page_title="Ask NBA AI",
    page_icon="🏀",
    initial_sidebar_state="collapsed",
)
st.title("Nikola Jokic vs Luka Doncic")

messages: list[Message] = [
    Message(
        role=Role.user,
        content=[
            TextMessage(
                text="Compare Nikola Jokic vs Luka Doncic in the 2024-25 season."
            )
        ],
    ),
    Message(
        role=Role.assistant,
        content=[
            TextMessage(
                text="In the 2024-25 NBA regular season, Luka Dončić is averaging more points per game, while Nikola Jokić is leading in rebounds and assists per game with significantly higher efficiency."
            ),
            DataMessage(
                title="##### 2024-25 Season Stats Comparison: Nikola Jokić vs Luka Dončić",
                glossary={
                    "PPG": "Points Per Game",
                    "RPG": "Rebounds Per Game",
                    "APG": "Assists Per Game",
                    "SPG": "Steals Per Game",
                    "BPG": "Blocks Per Game",
                    "FG%": "Field Goal Percentage",
                    "3P%": "Three-Point Percentage",
                },
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
            TextMessage(
                text=(
                    "### Context and Analysis\n\n"
                    "- **Scoring and Efficiency**: Luka Dončić is a slightly higher volume scorer, but Nikola Jokić is significantly more efficient from the field overall, particularly in field goal percentage, and has a better true shooting percentage (TS%).\n"
                    "- **Playmaking and Rebounding**: As expected from their positions (Jokić as a center, Dončić as a guard), Jokić has a clear advantage in rebounding, while both are elite passers, with Jokić currently holding a slight edge in assists per game this season.\n"
                    "- **Team Performance**: Both players have a significant impact on their respective teams. Jokić's Denver Nuggets had a 1-1 record versus Dončić's Los Angeles Lakers during the games they played against each other in the 2024-25 season.\n"
                    "- **Head-to-Head**: In two head-to-head games during the 2024-25 season, Jokić averaged 24.5 points, 15.5 rebounds, and 12.5 assists, while Dončić averaged 28.0 points, 9.5 rebounds, and 8.0 assists.\n\n"
                    "*Note: The 2024-25 NBA season concluded in June 2025. The data provided reflects the final statistics for that season.*"
                ),
            ),
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
    .st-key-message-user > div > div {
        flex-direction: row-reverse;
        text-align: right;
    }
</style>
""",
    unsafe_allow_html=True,
)

for message in messages:
    with st.container(key=f"message-{message.role.value}"):
        with st.chat_message(message.role):
            for msg in message.content:
                if isinstance(msg, TextMessage):
                    st.markdown(msg.text)

                elif isinstance(msg, DataMessage):
                    st.markdown(msg.title)

                    chat_tab, data_tab = st.tabs(["Chart", "Data"])
                    with data_tab:
                        df = make_df(msg.data, msg.columns)
                        st.dataframe(df, width="stretch")
                    with chat_tab:
                        st.bar_chart(df, sort=False, stack=False)

                    with st.expander("Glossary", expanded=False):
                        glossary_lines = [
                            f"- :small[**{term}**: {definition}]"
                            for term, definition in msg.glossary.items()
                        ]
                        glossary_md = "\n".join(glossary_lines)
                        st.markdown(glossary_md)


from streamlit_local_storage import LocalStorage

local_storage = LocalStorage()

if local_storage.getItem("user"):
    st.session_state.setdefault("default_open_dialog_index", 2)
else:
    st.session_state.setdefault("default_open_dialog_index", 0)

st.session_state.setdefault("open_dialog_index", None)
st.session_state.setdefault("is_email_valid", None)


def open_dialog(index: int):
    if index == 0:
        notify()
    elif index == 1:
        subscribe()
    elif index == 2:
        thanks()


@st.dialog("Welcome onboard!")
def thanks():
    st.success("Thanks — you'll hear from us soon!")

    with st.container(horizontal_alignment="right"):
        if st.button("Close"):
            st.session_state.open_dialog_index = None
            st.session_state.default_open_dialog_index = 2
            st.rerun()


@st.dialog("Get early access", dismissible=False)
def subscribe():
    st.markdown(
        """
        ### Your personal courtside AI is on the way! 🏀📊

        - Access player & team stats
        - Generate comparisons and interactive charts
        - Get data-driven insights and highlights
        - Discover new metrics and trends

        Leave your email for early access and enjoy **your first month of analytics FREE**!
    """
    )

    with st.form("subscribe_form", border=False):
        email = st.text_input("Email: ", placeholder="example@gmail.com")
        submitted = st.form_submit_button("Register")

        if submitted:
            is_valid_email = is_email(email, check_dns=True)

            if not email or not is_valid_email:
                st.warning("Please enter a valid email address.", icon="⚠️")
            else:
                logging.info(f"Registering email: {email}")

                local_storage.setItem("user", User(email=email).model_dump_json())

                st.session_state.open_dialog_index = 2

                st.rerun()


@st.dialog("Oops! We're not live yet...")
def notify():
    st.write(
        "... but we can't wait to show you what's coming! Sign up for early access!"
    )

    with st.container(horizontal_alignment="right"):
        if st.button("Next"):
            logging.info("User clicked 'Next' in the subscription dialog.")
            st.session_state.open_dialog_index = 1
            st.rerun()


st.caption("Suggestions")
for suggestion in suggestions:
    if st.button(suggestion.text):
        logging.info(f"Suggestion selected: {suggestion.text}")
        open_dialog(st.session_state.default_open_dialog_index)

st.caption("Knowledge cut-off: June 2025")

if prompt := st.chat_input("Ask me about NBA analytics..."):
    logging.info(f"User prompt: {prompt}")
    open_dialog(st.session_state.default_open_dialog_index)

open_dialog(st.session_state.open_dialog_index)

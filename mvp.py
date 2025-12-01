import sentry_sdk

sentry_sdk.init(
    dsn="https://072fd2564ff917a997fe783bc1ed30cc@o4509656915574784.ingest.de.sentry.io/4510461910253648",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)


import streamlit as st
import time

from models import Message, Suggestion, User


st.title("💬 NBA Analytics Agent")

messages: list[Message] = [
    Message(
        role="user",
        content="How did the Boston Celtics perform in the 2022-23 season?",
    ),
    Message(
        role="assistant",
        content="The Boston Celtics had a strong 2022-23 season, finishing with a 57-25 record and securing the 2nd seed in the Eastern Conference. They advanced to the Eastern Conference Finals but were eliminated by the Miami Heat in 7 games. Key players included Jayson Tatum and Jaylen Brown, who both averaged over 25 points per game.",
    ),
]
suggestions: list[Suggestion] = [
    Suggestion(text="📊 What was their win-loss record?"),
    Suggestion(text="⭐ Who were the standout players?"),
    Suggestion(text="🏀 How did they perform in the playoffs?"),
]

for message in messages:
    with st.chat_message(message.role):
        st.markdown(message.content)

st.chat_input("Ask me about NBA analytics...", disabled=True)

from streamlit_local_storage import LocalStorage

local_storage = LocalStorage()


@st.dialog("Get early access", dismissible=False)
def subscribe():
    st.write("Enter your email to get an early access! No spam — unsubscribe anytime.")

    email = st.text_input("Email: ", placeholder="example@gmail.com")

    is_valid_email = email and "@" in email and "." in email

    if email and not is_valid_email:
        st.info("Please enter a valid email to register.")

    if st.button("Register", disabled=not is_valid_email):
        print(f"Registering email: {email}")

        local_storage.setItem("user", User(email=email).to_json())
        st.success("Thanks — you'll hear from us soon!")

        time.sleep(2)
        st.rerun()


if not local_storage.getItem("user"):
    subscribe()

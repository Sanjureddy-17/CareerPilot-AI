
import streamlit as st
import requests
import os

try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except (KeyError, FileNotFoundError):
    BACKEND_URL = os.getenv(
        "BACKEND_URL",
        "http://127.0.0.1:8000"
    )

API_URL = f"{BACKEND_URL}/chat"
HISTORY_URL = f"{BACKEND_URL}/history"
CONVERSATIONS_URL = f"{BACKEND_URL}/conversations"


def load_history(conversation_id):
    response = requests.get(
        HISTORY_URL,
        params={"conversation_id": conversation_id},
        timeout=10
    )
    response.raise_for_status()
    return response.json().get("messages", [])

st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🤖",
    layout="centered"
)


try:
    response = requests.get(CONVERSATIONS_URL, timeout=10)
    response.raise_for_status()
    conversations = response.json().get("conversations", [])
except requests.RequestException:
    conversations = []
    st.warning("Could not load the saved conversations.")


if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.title("Your Chats")

    if st.button("➕ New Chat", use_container_width=True):
        try:
            response = requests.post(
                CONVERSATIONS_URL,
                timeout=10
            )
            response.raise_for_status()

            st.session_state.conversation_id = (
                response.json()["conversation_id"]
            )
            st.session_state.messages = []
            st.rerun()

        except requests.RequestException:
            st.error("Could not create a new conversation.")

    st.divider()

    for conversation in conversations:
        conversation_id = conversation["conversation_id"]
        title = conversation["title"]

        if st.button(
            title,
            key=f"chat_{conversation_id}",
            use_container_width=True
        ):
            st.session_state.conversation_id = conversation_id

            try:
                st.session_state.messages = load_history(
                    conversation_id
                )
                st.rerun()
            except requests.RequestException:
                st.error("Could not load this conversation.")



if st.session_state.conversation_id is None:
    if conversations:
        conversation_id = conversations[0]["conversation_id"]

        try:
            messages = load_history(conversation_id)

            st.session_state.conversation_id = conversation_id
            st.session_state.messages = messages

        except requests.RequestException:
            st.error("Could not load the latest conversation.")

    else:
        try:
            response = requests.post(
                CONVERSATIONS_URL,
                timeout=10
            )
            response.raise_for_status()

            st.session_state.conversation_id = (
                response.json()["conversation_id"]
            )
            st.session_state.messages = []

        except (requests.RequestException, KeyError, ValueError):
            st.error("Could not create a new conversation.")


st.title("CareerPilot AI")
st.caption("Your AI-powered career assistant")



for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input(
    "Ask about Python, resumes, skills, or interviews...",
    disabled=not st.session_state.conversation_id
)

if prompt:
    request_succeeded = False

    history = st.session_state.messages[-10:]

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("CareerPilot AI is thinking..."):

            try:
                response = requests.post(
                    API_URL,
                    json={
                        "conversation_id": st.session_state.conversation_id,
                        "message": prompt,
                        "history": history
                    },
                    timeout=60
                )

                response.raise_for_status()
                answer = response.json()["reply"]
                request_succeeded = True

            except requests.Timeout:
                answer = "The AI service took too long to respond. Please try again."

            except requests.ConnectionError:
                answer = "Cannot connect to CareerPilot AI. Please check whether the backend is running."


            except requests.HTTPError:
                if response.status_code == 404:
                    try:
                        # Create a fresh conversation
                        new_response = requests.post(
                            CONVERSATIONS_URL,
                            timeout=10
                        )
                        new_response.raise_for_status()

                        new_conversation_id = new_response.json()["conversation_id"]

                        st.session_state.conversation_id = new_conversation_id
                        st.session_state.messages = []

                        # Retry the original question with the new ID
                        retry_response = requests.post(
                            API_URL,
                            json={
                                "conversation_id": new_conversation_id,
                                "message": prompt,
                                "history": []
                            },
                            timeout=60
                        )
                        retry_response.raise_for_status()

                        answer = retry_response.json()["reply"]
                        request_succeeded = True

                    except (requests.RequestException, KeyError, ValueError):
                        answer = "Your previous conversation expired. Please start a new chat and try again."

                else:
                    try:
                        error_detail = response.json().get(
                            "detail",
                            "Unknown server error"
                        )
                    except ValueError:
                        error_detail = "The server returned an unexpected response."

                    answer = f"CareerPilot AI error ({response.status_code}): {error_detail}"

            except (ValueError, KeyError):
                answer = "The AI service returned an unexpected response."

            except requests.RequestException:
                answer = "A network error occurred. Please try again."

            st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    if request_succeeded:
        st.rerun()
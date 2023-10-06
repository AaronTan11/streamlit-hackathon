import streamlit as st
import requests
import json
from langchain.llms import HuggingFaceHub

# Set up API Token and URLs
API_TOKEN = HuggingFaceHub.huggingfacehub_api_token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
TEXT_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
IMAGE_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": f"Bearer {API_TOKEN}"}


def query(api_url, payload):
    data = json.dumps(payload)
    response = requests.post(api_url, headers=headers, data=data)
    if "generate" in payload["inputs"].lower():
        return {"image_data": response.content}
    else:  # Assuming text generation
        return json.loads(response.content.decode("utf-8"))


st.title("Chatbot with Text and Image Generation")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant-image":
            st.image(message["content"])
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Your input:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Determine API to use based on prompt
    api_url = IMAGE_API_URL if "generate" in prompt.lower() else TEXT_API_URL
    response_key = 'image_data' if "generate" in prompt.lower() else 'generated_text'
    role = "assistant-image" if "generate" in prompt.lower() else "assistant-text"

    with st.chat_message(role):
        api_response = query(api_url, {"inputs": prompt})
        if role == "assistant-image":
            st.image(api_response[response_key])
        else:
            st.markdown(api_response[response_key])
        st.session_state.messages.append(
            {"role": role, "content": api_response[response_key]})

import os
import random
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import time
from google.api_core.exceptions import ResourceExhausted, PermissionDenied
from googletrans import Translator
from PIL import Image
import uuid
from chat_db import init_db, save_message, load_history


# Initialize the translator and DB
translator = Translator()
init_db()

def translate_to_tamil(text):
    """Translate text to Tamil."""
    translation = translator.translate(text, dest='ta')  # 'ta' is the language code for Tamil
    return translation.text

st.title("I am your College Guide🌆🛬")




# Generate or get a unique user/session id
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

# Load chat history from DB
if "messages" not in st.session_state:
    history = load_history(st.session_state["user_id"])
    if not history:
        history = [{"role": "assistant", "content": "Hii 🤖, I'm here to help you"}]
    st.session_state.messages = history

if "last_request_time" not in st.session_state:
    st.session_state["last_request_time"] = 0.0

# Load API key and instructions from files
def load_api_key():
    """Load API key from environment variables or files."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key.strip()
    
    for candidate in ("key.txt", "mykey.txt"):
        try:
            with open(candidate, "r") as f:
                content = f.read().strip()
                if content:
                    return content
        except FileNotFoundError:
            continue
    return None

key = load_api_key()
if not key:
    st.error("API key not found. Set GEMINI_API_KEY env var or create key.txt/mykey.txt with your key.")
    st.stop()

with open("final.txt") as f:
    instructions = f.read()

# Configure the Generative AI model with fallback
genai.configure(api_key=key)
PREFERRED_MODEL = "gemini-1.5-pro-latest"
FALLBACK_MODEL = "gemini-1.5-flash-latest"

def create_model(name):
    return genai.GenerativeModel(
        model_name=name,
        system_instruction=instructions
    )

model = create_model(PREFERRED_MODEL)
fallback_model = create_model(FALLBACK_MODEL)

# Load and resize the image to optimize loading time
image = Image.open('logo1.png').resize((200, 200))

# Display the image at the top right
st.sidebar.image(image)
st.sidebar.title("Welcome to the CHATBOT of KEC")

# Contact Information in Sidebar
st.sidebar.title("Contact")
st.sidebar.markdown(
    """
    <a href="mailto:sabariramrp@gmail.com" class="button">Email</a><br>
    <a href="tel:+919489462870" class="button">Phone</a><br>
    <a href="https://kongu.ac.in/index.php" class="button">WEBSITE</a><br>
    """,
    unsafe_allow_html=True
)

# Language selection
language = st.sidebar.selectbox("Select Language", ["English", "Tamil"])

# Function to capture voice input with improved feedback and error handling
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = r.listen(source)
        try:
            user_input = r.recognize_google(audio)
            st.session_state.voice_input = user_input  # Store directly in session state
            st.write(f"You said: {user_input}")
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
            st.session_state.voice_input = None  # Clear if there's an error
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
            st.session_state.voice_input = None  # Clear if there's an error

# Improved AI response generation with better rate limiting and fallback
@st.cache_data(show_spinner=False)
def get_ai_response(user_input):
    """Generate AI response with fallback model and retry logic."""
    # Custom response for 'Who are you'
    if user_input.strip().lower() in ["who are you", "who are you?", "who r u", "who r u?"]:
        return "I am an AI assistant to handle admission queries about Kongu Engineering College."
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Try primary model first
            resp = model.generate_content(user_input)
            return resp.text
        except ResourceExhausted as e:
            last_error = e
            # Try fallback model immediately
            try:
                resp = fallback_model.generate_content(user_input)
                return resp.text
            except ResourceExhausted as e2:
                last_error = e2
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    sleep_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(sleep_time)
        except PermissionDenied as e:
            # Typically indicates quota not enabled or API not allowed
            raise e
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(1)
    
    # If all retries exhausted
    raise last_error if last_error else RuntimeError("Unknown error during generation")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Text input for user messages
user_input_text = st.chat_input("Type your message here...")

# Button for voice input; call function directly instead of threading
if st.button("Speak"):
    get_voice_input()  # Call function directly

# Determine which input to use (text or voice)
if user_input_text:
    user_input = user_input_text
elif 'voice_input' in st.session_state and st.session_state.voice_input is not None:
    user_input = st.session_state.voice_input
else:
    user_input = None


if user_input is not None:
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message(st.session_state["user_id"], "user", user_input)

    with st.chat_message("user"):
        st.write(user_input)

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Loading..."):
                # Throttle requests to avoid hitting rate limits
                min_interval = 2.0  # Minimum 2 seconds between requests
                now = time.time()
                last = st.session_state.get("last_request_time", 0.0)
                if now - last < min_interval:
                    time.sleep(min_interval - (now - last))

                try:
                    response_text = get_ai_response(user_input)
                    st.session_state["last_request_time"] = time.time()
                    
                    # Translate response based on selected language
                    if language == "Tamil":
                        response_text = translate_to_tamil(response_text)

                    st.write(response_text)
                    new_ai_message = {"role": "assistant", "content": response_text}
                    st.session_state.messages.append(new_ai_message)
                    save_message(st.session_state["user_id"], "assistant", response_text)
                except PermissionDenied:
                    st.error("❌ Access denied. Please check your API key has proper permissions and billing is enabled in Google AI Studio.")
                except ResourceExhausted:
                    st.error("⏳ Request limit exceeded. Please wait a moment and try again.")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

    # Clear voice input after processing
    if 'voice_input' in st.session_state:
        st.session_state.voice_input = None


# --- Sidebar: All Chat History in One Box ---
import sqlite3
st.sidebar.title("Chat History")

# Show all chat history for this user in a scrollable box
history = load_history(st.session_state["user_id"])
if history:
    with st.sidebar.expander("Show Chat History", expanded=False):
        chat_html = "<div style='max-height:300px; overflow-y:auto; border:1px solid #ddd; border-radius:8px; padding:10px; background:#18191a;'>"
        for msg in history:
            role = msg['role'].capitalize()
            content = msg['content']
            chat_html += f"<div style='border-radius:8px; border:1px solid #333; padding:8px; margin-bottom:8px; background-color:{'#23272f' if role=='User' else '#1a2636'};'>"
            chat_html += f"<b>{role}:</b><br>{content}"
            chat_html += "</div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)
else:
    st.sidebar.write("No chat history yet.")

# New Chat button
if st.sidebar.button("New Chat"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Hii 🤖, I'm here to help you"}]
    # Optionally clear DB for new session, or just clear UI
    st.rerun()

# Sidebar for FAQs based on dataset (pseudo-implementation)
faq_data = {
    "Is Hostels available in KEC?": "Yes, Hostels are available in KEC. 3 hostels for girls and 7 hostels for boys.",
    "How many Engineering courses are offered?": "14 Engineering Degrees",
}

st.sidebar.title("FAQs")
for question, answer in faq_data.items():
    if st.sidebar.button(question):
        st.sidebar.write(answer)
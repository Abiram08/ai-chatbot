import os
import time
import uuid
import sqlite3
import random
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted, PermissionDenied
from googletrans import Translator

# ==================================================================================================
# 1. CONFIGURATION & SETUP
# ==================================================================================================
# We load environment variables to keep sensitive keys secure.
load_dotenv()

def load_api_key():
    """
    Attempts to load the Google Gemini API key from various sources.
    Priority:
    1. Environment Variables (GEMINI_API_KEY or GOOGLE_API_KEY)
    2. Local file 'key.txt'
    """
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key.strip()
    
    # Fallback to checking a local file
    try:
        if os.path.exists("key.txt"):
            with open("key.txt", "r") as f:
                return f.read().strip()
    except Exception:
        pass
    return None

# Constants for the AI models
GEMINI_API_KEY = load_api_key()
PREFERRED_MODEL = "gemini-1.5-pro-latest"
FALLBACK_MODEL = "gemini-1.5-flash-latest"

# Initialize the Google Translator for multilingual support
translator = Translator()

# ==================================================================================================
# 2. DATABASE MANAGEMENT
# ==================================================================================================
# We use SQLite to store chat history locally so conversations persist across reloads.

def init_db():
    """Initializes the SQLite database and creates the table if it doesn't exist."""
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        role TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def save_message(user_id, role, content):
    """Saves a single message to the database."""
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

def load_history(user_id, limit=50):
    """
    Loads the last 'limit' messages for a specific user.
    We fetch in descending order (newest first) to get the latest, 
    then reverse it so it displays chronologically (oldest first).
    """
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

# ==================================================================================================
# 3. BOT LOGIC (AI & TRANSLATION)
# ==================================================================================================
# This section handles the intelligence: talking to Google Gemini and translating text.

def configure_genai(instructions):
    """
    Configures the Gemini AI models with the provided system instructions.
    Returns both a primary model and a fallback model (in case the primary is busy).
    """
    if not GEMINI_API_KEY:
        raise ValueError("API Key not found")
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    def create_model(name):
        return genai.GenerativeModel(
            model_name=name,
            system_instruction=instructions
        )

    model = create_model(PREFERRED_MODEL)
    fallback_model = create_model(FALLBACK_MODEL)
    return model, fallback_model

def translate_to_tamil(text):
    """Translates the given text to Tamil using Google Translate."""
    try:
        translation = translator.translate(text, dest='ta')
        return translation.text
    except Exception as e:
        # If translation fails, return original text to avoid crashing
        print(f"Translation error: {e}")
        return text

def get_ai_response(model, fallback_model, user_input):
    """
    Generates a response from the AI.
    Includes retry logic and fallback to a lighter model if the main one is overloaded.
    """
    # Hardcoded response for identity questions
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
            # If primary fails (quota/load), try fallback model immediately
            try:
                resp = fallback_model.generate_content(user_input)
                return resp.text
            except ResourceExhausted as e2:
                last_error = e2
                if attempt < max_retries - 1:
                    # Wait a bit before retrying (Exponential backoff)
                    sleep_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(sleep_time)
        except PermissionDenied as e:
            raise e
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(1)
    
    # If all retries fail, raise the last error
    raise last_error if last_error else RuntimeError("Unknown error during generation")

# ==================================================================================================
# 4. UI COMPONENTS
# ==================================================================================================
# Functions to handle the visual appearance and sidebar elements.

def load_css():
    """Injects custom CSS to style the app (Dark Mode theme)."""
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stChatInputContainer {
            padding-bottom: 20px;
        }
        .stChatMessage {
            background-color: #262730;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .stChatMessage[data-testid="stChatMessageUser"] {
            background-color: #2b313e;
        }
        .sidebar-content {
            padding: 20px;
        }
        .contact-button {
            display: inline-block;
            padding: 10px 20px;
            margin: 5px 0;
            background-color: #ff4b4b;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            text-align: center;
            width: 100%;
        }
        .contact-button:hover {
            background-color: #ff3333;
        }
        </style>
    """, unsafe_allow_html=True)

def setup_sidebar(logo_path):
    """Sets up the sidebar with logo, contact info, and language selection."""
    try:
        if os.path.exists(logo_path):
            image = Image.open(logo_path).resize((200, 200))
            st.sidebar.image(image)
    except Exception:
        st.sidebar.warning("Logo not found.")

    st.sidebar.title("Welcome to KEC Chatbot")
    
    # Contact Information
    st.sidebar.title("Contact")
    st.sidebar.markdown(
        """
        <a href="mailto:sabariramrp@gmail.com" class="contact-button">Email</a>
        <a href="tel:+919489462870" class="contact-button">Phone</a>
        <a href="https://kongu.ac.in/index.php" class="contact-button">Website</a>
        """,
        unsafe_allow_html=True
    )

    # Language selection
    language = st.sidebar.selectbox("Select Language", ["English", "Tamil"])
    return language

def display_chat_history_sidebar(history):
    """Displays the chat history in a scrollable box in the sidebar."""
    st.sidebar.title("Chat History")
    if history:
        with st.sidebar.expander("Show Chat History", expanded=False):
            chat_html = "<div style='max-height:300px; overflow-y:auto; border:1px solid #ddd; border-radius:8px; padding:10px; background:#18191a;'>"
            for msg in history:
                role = msg['role'].capitalize()
                content = msg['content']
                bg_color = '#23272f' if role == 'User' else '#1a2636'
                chat_html += f"<div style='border-radius:8px; border:1px solid #333; padding:8px; margin-bottom:8px; background-color:{bg_color};'>"
                chat_html += f"<b>{role}:</b><br>{content}"
                chat_html += "</div>"
            chat_html += "</div>"
            st.sidebar.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.sidebar.write("No chat history yet.")

def display_faqs():
    """Displays a list of Frequently Asked Questions in the sidebar."""
    faq_data = {
        "Is Hostels available in KEC?": "Yes, Hostels are available in KEC. 3 hostels for girls and 7 hostels for boys.",
        "How many Engineering courses are offered?": "14 Engineering Degrees",
    }
    st.sidebar.title("FAQs")
    for question, answer in faq_data.items():
        if st.sidebar.button(question):
            st.sidebar.info(answer)

# ==================================================================================================
# 5. MAIN APPLICATION
# ==================================================================================================
# The entry point of the Streamlit application.

def main():
    # Initialize DB
    init_db()

    # Page configuration
    st.set_page_config(page_title="KEC Chatbot", page_icon="🤖", layout="wide")

    # Load CSS
    load_css()

    # Session State Initialization
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())

    if "messages" not in st.session_state:
        history = load_history(st.session_state["user_id"])
        if not history:
            history = [{"role": "assistant", "content": "Hii 🤖, I'm here to help you"}]
        st.session_state.messages = history

    if "last_request_time" not in st.session_state:
        st.session_state["last_request_time"] = 0.0

    # Load Instructions
    try:
        with open("final.txt", "r") as f:
            instructions = f.read()
    except FileNotFoundError:
        st.error("Error: final.txt not found. Please ensure the instructions file is present.")
        st.stop()

    # Configure AI
    try:
        model, fallback_model = configure_genai(instructions)
    except ValueError:
        st.error("API key not found. Please set GEMINI_API_KEY in .env or environment variables.")
        st.stop()

    # Sidebar Setup
    language = setup_sidebar("logo1.png")
    display_chat_history_sidebar(load_history(st.session_state["user_id"]))
    display_faqs()

    # Main Chat Interface
    st.title("I am your College Guide 🌆🛬")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Voice Input Function
    def get_voice_input():
        r = sr.Recognizer()
        with sr.Microphone() as source:
            with st.spinner("Listening..."):
                try:
                    audio = r.listen(source, timeout=5)
                    user_input = r.recognize_google(audio)
                    return user_input
                except sr.UnknownValueError:
                    st.error("Sorry, I could not understand the audio.")
                except sr.RequestError as e:
                    st.error(f"Could not request results; {e}")
                except Exception:
                    st.error("No audio detected.")
        return None

    # Input Area
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input_text = st.chat_input("Type your message here...")
    with col2:
        if st.button("🎤 Speak"):
            voice_input = get_voice_input()
            if voice_input:
                user_input_text = voice_input

    # Process Input
    if user_input_text:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input_text})
        save_message(st.session_state["user_id"], "user", user_input_text)
        with st.chat_message("user"):
            st.write(user_input_text)

        # Generate AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Rate limiting to avoid hitting API limits
                min_interval = 2.0
                now = time.time()
                last = st.session_state.get("last_request_time", 0.0)
                if now - last < min_interval:
                    time.sleep(min_interval - (now - last))
                
                try:
                    response_text = get_ai_response(model, fallback_model, user_input_text)
                    st.session_state["last_request_time"] = time.time()
                    
                    # Translate if needed
                    if language == "Tamil":
                        response_text = translate_to_tamil(response_text)
                    
                    st.write(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    save_message(st.session_state["user_id"], "assistant", response_text)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

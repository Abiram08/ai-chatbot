import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import time
from google.api_core.exceptions import ResourceExhausted
from googletrans import Translator
from PIL import Image

# Initialize the translator
translator = Translator()

def translate_to_tamil(text):
    """Translate text to Tamil."""
    translation = translator.translate(text, dest='ta')  # 'ta' is the language code for Tamil
    return translation.text

st.title("I am your College Guide🌆🛬")

# Initialize session state for memory and messages
if "memory" not in st.session_state:
    st.session_state["memory"] = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hii 🤖, I'm here to help you"}
    ]

# Load API key and instructions from files
with open('mykey.txt') as f:
    key = f.read()

with open("final.txt") as f:
    instructions = f.read()

# Configure the Generative AI model
genai.configure(api_key=key)
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    system_instruction=instructions
)

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

# Caching AI response generation to speed up repeated queries
@st.cache_data(show_spinner=False)
def get_ai_response(user_input):
    return model.generate_content(user_input)

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

    with st.chat_message("user"):
        st.write(user_input)

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Loading..."):
                max_retries = 5  # Set maximum number of retries
                for attempt in range(max_retries):
                    try:
                        ai_response = get_ai_response(user_input)  # Cached function call
                        break  # Exit loop if successful
                    except ResourceExhausted:
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # Exponential backoff strategy
                            time.sleep(wait_time)
                        else:
                            st.error("Request limit exceeded. Please try again later.")
                            ai_response = None

                if ai_response is not None:
                    response_text = ai_response.text
                    
                    # Translate response based on selected language
                    if language == "Tamil":
                        response_text = translate_to_tamil(response_text)

                    st.write(response_text)

                    new_ai_message = {"role": "assistant", "content": response_text}
                    st.session_state.messages.append(new_ai_message)

# Sidebar for FAQs based on dataset (pseudo-implementation)
faq_data = {
    "Is Hostels available in KEC?": "Yes, Hostels are available in KEC. 3 hostels for girls and 7 hostels for boys.",
    "How many Engineering courses are offered?": "14 Engineering Degrees",
}

st.sidebar.title("FAQs")
for question, answer in faq_data.items():
    if st.sidebar.button(question):
        st.sidebar.write(answer)

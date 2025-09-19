# AI ChatBot

This project is a Streamlit-based AI chatbot that uses Google Gemini models for conversational AI, supports voice input, and can translate responses to Tamil. It is designed as a college guide assistant.

## Features
- Chat interface with memory
- Voice input using microphone
- Google Gemini AI integration
- Language translation (English/Tamil)
- Sidebar with contact info and FAQs

## Prerequisites
- Python 3.8 or higher
- A Google Gemini API key (or Google Generative AI key)

## Setup Instructions

1. **Clone the repository:**

```powershell
git clone https://github.com/Abiram08/ai-chatbot.git
cd "ai-chatbot"
```

2. **Install dependencies:**

```powershell
pip install -r requirements.txt
```

3. **Add your API key:**
- Place your Gemini API key in a file named `key.txt` or `mykey.txt` in the project directory, **or**
- Set the environment variable `GEMINI_API_KEY` or `GOOGLE_API_KEY` with your key.

4. **Run the chatbot:**

```powershell
streamlit run ftest.py
```

5. **Usage:**
- Open the provided local URL in your browser.
- Interact via text or click "Speak" for voice input.
- Use the sidebar to select language, view contact info, and see FAQs.

## Contact

- Email: nellaiabiram08@gmail.com

## Notes
- Ensure your microphone is enabled for voice input.
- The chatbot uses `logo1.png` for branding in the sidebar.
- For translation, Google Translate API is used via `googletrans`.

## Troubleshooting
- If you see API key errors, check your key file or environment variable.
- For package issues, ensure all dependencies are installed.
- For voice input errors, check your microphone and permissions.

## License
This project is for educational/demo purposes.

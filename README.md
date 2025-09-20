
# Kongu Engineering College Admission Chatbot

This project is an AI-powered chatbot designed to answer queries and clarify doubts related to admissions at **Kongu Engineering College**. The chatbot provides information about courses, eligibility, application procedures, campus facilities, and other admission-related topics to assist prospective students and their parents.

## Features
- Answers frequently asked questions about Kongu Engineering College admissions
- Provides details on courses, eligibility, and application process
- Clarifies doubts about campus life, facilities, and more
- User-friendly and interactive interface

## Prerequisites
- Python 3.8 or higher
- A Google Gemini API key (or Google Generative AI key)

## Setup Instructions

1. **Install dependencies:**
	```powershell
	pip install -r requirements.txt
	```

2. **Add your API key:**
	- Place your Gemini API key in a file named `key.txt` or `mykey.txt` in the project directory, **or**
	- Set the environment variable `GEMINI_API_KEY` or `GOOGLE_API_KEY` with your key.

3. **Run the chatbot:**
	```powershell
	streamlit run ftest.py
	```

## Important Notice
**This repository is intended solely for the use of Kongu Engineering College.**


If you have questions about this project, please contact the repository owner.

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

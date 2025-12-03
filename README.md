# Kongu Engineering College Admission Chatbot

This project is an AI-powered chatbot designed to answer queries and clarify doubts related to admissions at **Kongu Engineering College**. The chatbot provides information about courses, eligibility, application procedures, campus facilities, and other admission-related topics.

## Features
- **AI-Powered:** Uses Google's Gemini models for intelligent responses.
- **Multilingual:** Supports English and Tamil (via translation).
- **Voice Support:** Allows voice input for queries.
- **Chat History:** Saves and displays recent chat history.
- **FAQs:** Quick access to frequently asked questions.

## Prerequisites
- Python 3.8 or higher
- A Google Gemini API key

## Setup Instructions

1. **Install dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```

2. **Configure API Key:**
    - Create a `.env` file in the project directory.
    - Add your API key:
      ```
      GEMINI_API_KEY=your_api_key_here
      ```
    - Alternatively, you can use `key.txt`.

3. **Run the chatbot:**
    ```powershell
    streamlit run app.py
    ```

## Project Structure
- `app.py`: The main application file containing all logic, UI, and configuration.
- `final.txt`: System instructions for the AI.
- `key.txt`: (Optional) File to store your API key.
- `requirements.txt`: List of dependencies.

## Contact
- Email: nellaiabiram08@gmail.com

## License
This project is for educational/demo purposes.

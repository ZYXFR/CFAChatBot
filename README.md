# CFA Chatbot Application

## 🧠 Overview

This AI-powered chatbot helps users explore CFA-related topics, including:

- 📚 Exam content and curriculum details
- 🏛️ Foundational knowledge (finance, ethics, economics)
- 📅 CFA France events and announcements

Built using **OpenAI GPT**, **Streamlit**, and modular Python code.

---

## 🛠️ Prerequisites

Before running the app, make sure you have:

- ✅ Python 3.9 or higher
- ✅ `pip` package manager
- ✅ Virtual environment tool (`venv`, `virtualenv`, or `conda`)
- ✅ OpenAI API Key (get one at [OpenAI](https://platform.openai.com/signup))

---

## ⚙️ 1. Set Up Environment

### Step 1: Clone the Repository

```bash
git clone https://github.com/ZYXFR/CFAChatBot.git
cd CFAChatBot
```

## ⚙️ 2: Create and Activate Virtual Environment

# Create

python3 -m venv venv

# Activate (macOS/Linux)

source venv/bin/activate

# Activate (Windows)

venv\Scripts\activate

## ⚙️ 3: Install Dependencies

pip install -r requirements.txt

## ⚙️ 4: Run application

streamlit run main.py
http://localhost:8501

## ⚙️ 5: Project Structure

CFAChatBot/
├── main.py                # Streamlit app entry point
├── requirements.txt       # Dependency list
├── .env                   # API key (not committed)
├── .env.example           # Example env file format
├── src/
│   ├── PROMPTS/           # Prompt engineering files
│   └── utils/             # Helper functions
└── venv/                  # Local Python virtual environment





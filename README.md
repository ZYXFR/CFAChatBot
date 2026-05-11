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

## ⚙️ Setup and Run

### 1) Clone the repository

```bash
git clone https://github.com/ZYXFR/CFAChatBot.git
cd CFAChatBot
```

### 2) Create a virtual environment (first time only)

```bash
python3 -m venv venv
```

This creates one local environment folder named `venv`.

### 3) Activate the virtual environment

**macOS/Linux**

```bash
source venv/bin/activate
```

**Windows (PowerShell)**

```powershell
venv\Scripts\Activate.ps1
```

**Windows (cmd)**

```cmd
venv\Scripts\activate
```

### 4) Install dependencies

```bash
pip install -r requirements.txt
```

### 5) Run the app

```bash
streamlit run main.py
```

Open:

`http://localhost:8501`

---

## 🔁 Starting the app again later

You do **not** need to create a new virtual environment every time.

When you restart your computer or open a new terminal, run:

```bash
cd CFAChatBot
source venv/bin/activate
streamlit run main.py
```

---

## ❓Do I need to recreate `venv`?

Usually, **no**.

Recreate `venv` only if:

- the `venv` folder was deleted
- you changed Python major/minor version
- the environment is broken and packages cannot be imported

If `venv` exists, running `python3 -m venv venv` targets the same folder (`venv`), not a new random one.

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





# CFA Chatbot Application

## Getting Started

This application is designed to help users explore CFA-related topics, including exam details, foundational knowledge, and CFA France events, using OpenAI’s GPT model.

### Prerequisites

1. **Install Python**: Ensure you have Python 3.9 or higher installed on your machine.
2. **Install Virtual Environment Tools**: Use `venv` or another virtual environment manager like `virtualenv`.

---

### 1. Setting Up the Environment

#### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone <repository-url>
cd CFAChatBot
```

Step 2: Create a Virtual Environment

Create a virtual environment to isolate dependencies:

</code></div></div></pre>

Activate the virtual environment:

* On Linux/macOS:
  </code></div></div></pre>
* On Windows:
  </code></div></div></pre>

#### Step 3: Install Required Packages

Install all dependencies specified in `requirements.txt`:

</code></div></div></pre>

---

### 2. Configuring the Environment

#### Step 1: Set Up OpenAI API Key

Create a `.env` file in the project’s root directory and add your OpenAI API key:

</code></div></div></pre>

> **Note**: Replace `your_openai_api_key_here` with your actual OpenAI API key. If you don’t have an API key, sign up at [OpenAI](https://platform.openai.com/signup/).

---

### 3. Running the Application

Run the application using Streamlit:

</code></div></div></pre>

After running the command, the application will be accessible in your browser at:

</code></div></div></pre>

---

### Example Workflow

1. Open the application in your browser.
2. Select the type of question you want to ask from the sidebar (e.g., Exam Details, Foundational Knowledge, or CFA France Events).
3. Enter your question in the input box and click "Submit."
4. View the generated response and explore related questions.

---

### 4. Deactivating the Virtual Environment

Once done, deactivate the virtual environment:

</code></div></div></pre>

---

### Troubleshooting

1. **Error: Missing Dependencies**
   Ensure all dependencies are installed by running:
   </code></div></div></pre>
2. **Error: Missing OpenAI API Key**
   Make sure your `.env` file contains the correct `OPENAI_API_KEY`.
3. **Streamlit Not Found**
   Ensure the virtual environment is activated and dependencies are installed.

---

### 5. File Structure

├── main.py                 # Entry point for the application
├── src/
│   ├── PROMPTS/            # Prompt definitions
│   └── utils/              # Utility scripts
├── requirements.txt        # Dependency list
├── README.md               # Project documentation
├── .env                    # Environment variables
└── venv/                   # Virtual environment (generated locally)</code></div></div></pre>

```

```

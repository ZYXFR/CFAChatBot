# CFA Chatbot Step-by-Step Runbook

This runbook is designed for repeatable startup and operation checks.

## 0) Open terminal and go to project

```bash
cd /home/yzhao/projects/RD/CFAChatBot
pwd
```

Expected:
- Current directory is `/home/yzhao/projects/RD/CFAChatBot`

Record:
- Date/time:
- Operator:
- `pwd` output:

---

## 1) Activate project environment (Conda)

```bash
conda activate cfa-chatbot
```

If `cfa-chatbot` does not exist yet, create it first:

```bash
conda create -n cfa-chatbot python=3.11 -y
conda activate cfa-chatbot
```

Record:
- Active env name:
- `python --version`:
- `which python`:

---

## 2) Verify required environment variable

Project requires `.env` with:

```env
OPENAI_API_KEY=your_key_here
```

Quick check:

```bash
test -f .env && echo ".env exists" || echo ".env missing"
```

Record:
- `.env` status:
- API key configured: yes/no

---

## 3) Install/update dependencies

```bash
python -m pip install -r requirements.txt
```

Important:
- After pulling new code, always run this command again.
- If a new package is added (example: `pypdf` for PDF RAG), the app may fail until dependencies are reinstalled.

Record:
- Install finished: yes/no
- Errors (if any):

---

## 4) Start app

```bash
streamlit run main.py
```

Expected:
- Terminal shows local URL, usually `http://localhost:8501`

Record:
- Startup time:
- Local URL:
- Any warning/error:

---

## 5) Smoke test checklist

After opening the page:
- [ ] Sidebar function selector is visible
- [ ] Can submit a question
- [ ] Response is returned
- [ ] Chat history is visible
- [ ] `chat_log.jsonl` is updated

Record:
- Passed checks:
- Failed checks:
- Notes:

---

## 6) Stop app

In the terminal running Streamlit:
- Press `Ctrl + C`

Record:
- Shutdown time:
- Clean exit: yes/no

---

## 7) Optional quick diagnostics commands

```bash
echo $CONDA_DEFAULT_ENV
python --version
which python
python -c "import openai, streamlit; print('openai ok, streamlit ok')"
```

Use these when startup fails.

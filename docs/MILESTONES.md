# CFA France Chatbot Milestones

This project is managed with milestone gates. Each milestone must pass a check before moving to the next one.

## M0 - Project Foundation

Goal: Make the project runnable, stable, and ready for iterative feature delivery.

Scope:
- Dependency compatibility baseline
- Environment and secret management baseline
- Repository hygiene baseline
- Milestone check process setup

Gate checks:
- [ ] `pip install -r requirements.txt` completes without dependency conflicts
- [ ] `.env` is no longer committed; `.env.example` exists
- [ ] Build/runtime artifacts are ignored (`__pycache__`, logs, local env files)
- [ ] App starts with `streamlit run main.py`
- [ ] This milestone document is updated with outcomes

Evidence to record:
- Python version used
- Install output snapshot
- Startup output snapshot
- Known issues left for M1

Decision:
- Pass -> continue to M1 (Q&A + basic RAG)
- Fail -> fix blocking items, rerun checks

M0 execution status (today):
- [x] `pip install -r requirements.txt` completes without dependency conflicts
- [x] `.env` is no longer tracked; `.env.example` created
- [x] Runtime artifacts are ignored with `.gitignore`
- [x] App starts with `streamlit run main.py`
- [x] Milestone process document created

---

## M1 - Q&A + Basic RAG

Goal: Deliver a reliable CFA knowledge assistant with traceable answers.

Gate checks:
- [ ] User can ask CFA question and get answer
- [ ] Answers include source citations when context is retrieved
- [ ] Fallback behavior is clear when no source found
- [ ] Multi-turn context works in one session

M1 execution status (in progress):
- [x] Local knowledge base folder created (`knowledge_base/`)
- [x] Basic retrieval pipeline wired to `main.py`
- [x] Retrieved source names are shown in chat history
- [ ] Manual QA with 10 sample questions

## M2 - Official Events Sync

Goal: Show latest CFA France activities from official sources.

Gate checks:
- [ ] Data fetch job parses at least one official page
- [ ] Events are stored in structured format
- [ ] UI shows latest events and last sync time
- [ ] Query like "latest events" returns grounded results

M2 execution status (in progress):
- [x] Implemented CFA France homepage fetch + parser (`src/events_sync.py`)
- [x] Added local cache storage (`data/events_cache.json`)
- [x] Connected Events Hub UI with refresh button and sync timestamp
- [x] Event-grounded Q&A path for event-style queries (uses official feed + localized display)
- [x] UI languages (EN/FR/ZH) + LLM localize/enrich events (speaker + highlights)

## M3 - Quiz and Practice

Goal: Provide a basic mock test flow for learning.

Gate checks (MVP):
- [x] Load question set
- [x] User can submit answers
- [x] Score and explanations are shown
- [x] Wrong answers are captured for review

M3 execution status (MVP done):
- [x] Demo question set JSON (`knowledge_base/quiz_level1_demo.json`)
- [x] Loader + grader (`src/quiz.py`)
- [x] Quiz Lab tab: form, submit, score, per-item explanation (EN/FR/ZH UI labels)
- [x] Reset clears answers and last result

## M4 - Fancy UI and Storytelling

Goal: Deliver a polished visual experience suitable for showcase.

Gate checks:
- [ ] Unified visual theme across pages
- [ ] Hero section and high-impact landing experience
- [ ] Smooth interactions and responsive layout
- [ ] Demo path can be completed in under 3 minutes

## M5 - Teaching Package (1 hour workshop)

Goal: Turn this project into a reusable hands-on teaching module.

Gate checks:
- [ ] PPT outline complete
- [ ] Demo script with timing complete
- [ ] Checkpoint tags/versions mapped to lesson flow
- [ ] Student exercise tasks and answer key ready

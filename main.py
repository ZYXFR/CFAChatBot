import streamlit as st
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
import sys
from dataclasses import asdict
from datetime import datetime
import json

# Load .env file
load_dotenv()

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment. Please check your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Completion length (default raised; was 500 and truncated long CFA answers)
MAX_COMPLETION_TOKENS = int(os.getenv("OPENAI_MAX_COMPLETION_TOKENS", "2500"))

# Official homepage scrape: Streamlit in-process cache (minutes)
_EVENTS_SCRAPE_TTL_SECONDS = max(60, int(os.getenv("EVENTS_HOMEPAGE_CACHE_MINUTES", "360"))) * 60

# LLM enrich/translate for events: disk cache TTL (hours); same snapshot + lang skips API until expiry
_EVENTS_ENRICH_TTL_SECONDS = max(1, int(os.getenv("EVENTS_ENRICH_CACHE_TTL_HOURS", "168"))) * 3600

# Dynamically load PYTHONPATH
pythonpath = os.getenv("PYTHONPATH")
if pythonpath and pythonpath not in sys.path:
    sys.path.append(pythonpath)

from src.PROMPTS import PROMPTS  # Prompt dictionary or functions
from src import i18n
from src.events_display import enrich_and_localize, fallback_display
from src.events_enrich_cache import load_enriched_display, save_enriched_display
from src.quiz import grade, load_questions
from src.quiz_ai import analyze_wrong_items, explain_all_questions, generate_practice_from_wrong
from src.events_sync import EventItem, EventsPayload, UpdateItem, fetch_events_payload, load_cached_payload, save_payload
from src.rag import build_chunks, build_chunks_from_uploaded_files, format_context, retrieve_chunks


CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    .stApp {
        background:
            radial-gradient(1200px 500px at 8% -8%, rgba(58, 101, 255, 0.22), transparent 62%),
            radial-gradient(900px 420px at 94% 0%, rgba(214, 164, 88, 0.14), transparent 58%),
            linear-gradient(160deg, #060913 0%, #0b1122 48%, #060913 100%);
        color: #e8ecff;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.1px;
    }
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }
    .hero-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(130deg, rgba(13, 24, 53, 0.82), rgba(8, 13, 30, 0.86));
        border: 1px solid rgba(157, 182, 255, 0.24);
        border-radius: 18px;
        padding: 28px 30px;
        margin-bottom: 16px;
        box-shadow: 0 20px 45px rgba(3, 5, 12, 0.5);
        backdrop-filter: blur(6px);
    }
    .hero-card::before {
        content: "";
        position: absolute;
        inset: -120px -60px auto auto;
        width: 360px;
        height: 360px;
        background: radial-gradient(circle, rgba(101, 138, 255, 0.28), transparent 65%);
        pointer-events: none;
    }
    .hero-title {
        margin: 0;
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #f4f7ff;
        letter-spacing: 0.4px;
    }
    .hero-subtitle {
        color: #c1cffd;
        font-size: 1rem;
        margin-top: 0.55rem;
        max-width: 880px;
    }
    .hero-badges {
        margin-top: 0.95rem;
    }
    .hero-badge {
        display: inline-block;
        border: 1px solid rgba(230, 194, 119, 0.55);
        border-radius: 999px;
        padding: 4px 11px;
        margin: 0 8px 6px 0;
        font-size: 0.77rem;
        color: #f7e5bc;
        background: rgba(66, 48, 19, 0.32);
    }
    .status-card {
        border: 1px solid rgba(148, 175, 255, 0.23);
        border-radius: 16px;
        padding: 14px 16px;
        background: linear-gradient(140deg, rgba(12, 20, 42, 0.88), rgba(7, 11, 24, 0.88));
        margin-bottom: 10px;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 10px 24px rgba(3, 6, 15, 0.45);
    }
    .status-k {
        font-size: 0.78rem;
        color: #9cafef;
        margin-bottom: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.75px;
    }
    .status-v {
        font-size: 1.08rem;
        font-weight: 600;
        color: #eaf0ff;
    }
    .answer-frame {
        border-left: 3px solid #7f9dff;
        background: linear-gradient(130deg, rgba(10, 18, 38, 0.86), rgba(7, 12, 26, 0.9));
        border-radius: 12px;
        padding: 11px 14px;
        margin: 8px 0 10px 0;
        box-shadow: 0 9px 24px rgba(3, 6, 16, 0.36);
    }
    .module-header {
        border: 1px solid rgba(228, 194, 120, 0.38);
        background: linear-gradient(120deg, rgba(36, 49, 91, 0.85), rgba(10, 15, 31, 0.88));
        border-radius: 14px;
        padding: 10px 14px;
        margin: 8px 0 14px 0;
        color: #f8e7bf;
        font-weight: 600;
        letter-spacing: 0.2px;
    }
    .source-chip {
        display: inline-block;
        border: 1px solid rgba(169, 191, 255, 0.56);
        border-radius: 999px;
        padding: 2px 10px;
        margin: 4px 6px 0 0;
        font-size: 0.82rem;
        color: #e6edff;
        background: rgba(23, 34, 67, 0.92);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(8, 12, 25, 0.72);
        border-radius: 12px;
        padding: 6px;
        border: 1px solid rgba(146, 172, 255, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        height: 38px;
        color: #bfd0ff;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg, rgba(66, 97, 189, 0.55), rgba(31, 49, 106, 0.65)) !important;
        color: #f4f7ff !important;
    }
    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(149, 177, 255, 0.42);
        background: linear-gradient(120deg, #3d61d3, #2b469f);
        color: #f5f8ff;
        font-weight: 600;
        box-shadow: 0 8px 22px rgba(36, 58, 138, 0.5);
    }
    .stButton > button:hover {
        border-color: rgba(201, 217, 255, 0.75);
        background: linear-gradient(120deg, #4a70e5, #3354be);
        transform: translateY(-1px);
    }
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(136, 162, 240, 0.38) !important;
        background: rgba(9, 15, 31, 0.92) !important;
        color: #f0f4ff !important;
    }
</style>
"""


PRO_MODE_INSTRUCTIONS = """
You are running in CFA Pro Mode for CFA France.

Professional rules:
1. Prioritize CFA-specific and curriculum-aligned explanations.
2. If retrieved sources are available, ground your answer in them and cite [Source N].
3. If sources are missing or weak, explicitly say the answer is general guidance.
4. Never provide personalized investment advice or guaranteed outcomes.
5. For policy, exam windows, membership, or event logistics, recommend checking official CFA Institute or CFA France pages.
6. Keep tone professional, concise, and educational.
"""


GENERAL_MODE_INSTRUCTIONS = """
You are running in General Mode.
Give a helpful high-level answer and clearly state when details should be verified with official CFA sources.
"""

EVENT_QUERY_KEYWORDS = {
    "event",
    "events",
    "upcoming",
    "latest events",
    "society event",
    "activity",
    "activities",
    "announcement",
    "announcements",
}
EVENT_QUERY_KEYWORDS_ZH = ("活动", "事件", "公告", "最新", "协会", "日程")
EVENT_QUERY_KEYWORDS_FR = (
    "événement",
    "evenement",
    "évènements",
    "actualité",
    "actualités",
    "annonces",
    "prochain",
)


def save_log(function, question, answer, filename="chat_log.jsonl"):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "function": function,
        "question": question,
        "answer": answer
    }
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def query_openai(prompt, user_input):
    """
    Calls OpenAI API with the given prompt and user input.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
            max_tokens=MAX_COMPLETION_TOKENS,
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        st.error(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
        return None


def query_openai_stream(prompt, user_input):
    """
    Calls OpenAI API using streaming mode.
    Yields content chunks as they arrive.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
            max_tokens=MAX_COMPLETION_TOKENS,
            stream=True  # ✅ 关键：启用流式输出
        )

        full_response = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                yield delta  # 每次返回新增字符
        return full_response

    except OpenAIError as e:
        yield f"\n\n[OpenAI API Error]: {e}"
    except Exception as e:
        yield f"\n\n[Unexpected Error]: {e}"


@st.cache_resource
def get_knowledge_chunks():
    return build_chunks("knowledge_base")


def render_status_card(title: str, value: str):
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-k">{title}</div>
            <div class="status-v">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_chips(sources, lang: str):
    if not sources:
        st.caption(i18n.t(lang, "no_sources"))
        return

    chips_html = "".join([f"<span class='source-chip'>{source}</span>" for source in sources])
    st.markdown(chips_html, unsafe_allow_html=True)


@st.cache_data(ttl=_EVENTS_SCRAPE_TTL_SECONDS)
def get_latest_events_payload():
    payload = fetch_events_payload()
    save_payload(payload)
    return payload


def is_events_query(user_input: str) -> bool:
    lowered = user_input.lower()
    if any(keyword in lowered for keyword in EVENT_QUERY_KEYWORDS):
        return True
    if any(keyword in user_input for keyword in EVENT_QUERY_KEYWORDS_ZH):
        return True
    if any(keyword in lowered for keyword in EVENT_QUERY_KEYWORDS_FR):
        return True
    return False


def serialize_payload(payload: EventsPayload) -> str:
    return json.dumps(
        {
            "source_url": payload.source_url,
            "synced_at": payload.synced_at,
            "events": [asdict(e) for e in payload.events],
            "updates": [asdict(u) for u in payload.updates],
        },
        sort_keys=True,
        ensure_ascii=False,
    )


def deserialize_payload(snapshot: str) -> EventsPayload:
    data = json.loads(snapshot)
    return EventsPayload(
        source_url=data["source_url"],
        synced_at=data["synced_at"],
        events=[EventItem(**item) for item in data.get("events", [])],
        updates=[UpdateItem(**item) for item in data.get("updates", [])],
    )


def get_cached_display_events(snapshot: str, lang: str) -> dict:
    """Use disk cache when source snapshot unchanged and TTL not expired; avoids daily LLM repeats."""
    cached = load_enriched_display(snapshot, lang, _EVENTS_ENRICH_TTL_SECONDS)
    if cached is not None:
        return cached

    payload = deserialize_payload(snapshot)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        display_events, display_updates = fallback_display(payload, lang)
    else:
        openai_client = OpenAI(api_key=api_key)
        display_events, display_updates = enrich_and_localize(payload, lang, openai_client)
    result = {
        "events": [asdict(item) for item in display_events],
        "updates": [asdict(item) for item in display_updates],
    }
    save_enriched_display(snapshot, lang, result)
    return result


def rows_for_events_payload(snapshot: str, lang: str, use_ai_enrich: bool) -> dict:
    """Default: scraped text only. AI translate/enrich runs only when use_ai_enrich is True."""
    if use_ai_enrich:
        return get_cached_display_events(snapshot, lang)
    payload = deserialize_payload(snapshot)
    display_events, display_updates = fallback_display(payload, lang)
    return {
        "events": [asdict(item) for item in display_events],
        "updates": [asdict(item) for item in display_updates],
    }


def build_events_answer_markdown(payload: EventsPayload, display_rows: dict, lang: str) -> str:
    def tr(key: str) -> str:
        return i18n.t(lang, key)

    lines = [
        f"## {tr('events_answer_title')}",
        "",
        f"- {tr('last_synced')}: {payload.synced_at}",
        f"- {tr('official_source')}: {payload.source_url}",
        "",
        f"### {tr('upcoming_events')}",
    ]

    events = display_rows.get("events", [])
    if events:
        for event in events[:5]:
            lines.append(f"- **{event.get('title', '')}**")
            lines.append(f"  - {tr('schedule')}: {event.get('schedule', '')}")
            lines.append(f"  - {tr('location')}: {event.get('location', '')}")
            lines.append(f"  - {tr('speaker')}: {event.get('speaker', '')}")
            for highlight in event.get("highlights", [])[:4]:
                lines.append(f"  - • {highlight}")
    else:
        lines.append(f"- {tr('no_events')}")

    lines.append("")
    lines.append(f"### {tr('latest_updates')}")
    updates = display_rows.get("updates", [])
    if updates:
        for update in updates[:4]:
            lines.append(f"- **{update.get('title', '')}**: {update.get('summary', '')}")
    else:
        lines.append(f"- {tr('no_updates')}")

    lines.append("")
    lines.append(tr("verify_official"))
    return "\n".join(lines)


def main():
    st.set_page_config(page_title="CFA France Assistant", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    lang_labels = ["English", "Français", "中文"]
    lang_codes = {"English": "en", "Français": "fr", "中文": "zh"}
    lang_pick = st.sidebar.selectbox("Interface language / Langue / 界面语言", lang_labels, index=0)
    lang = lang_codes[lang_pick]

    def tr(key: str) -> str:
        return i18n.t(lang, key)

    st.markdown(
        f"""
        <div class="hero-card">
            <h2 class="hero-title">{tr("hero_title")}</h2>
            <div class="hero-subtitle">{tr("hero_subtitle")}</div>
            <div class="hero-badges">
                <span class="hero-badge">{tr("badge_cfa")}</span>
                <span class="hero-badge">{tr("badge_source")}</span>
                <span class="hero-badge">{tr("badge_exam")}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    knowledge_chunks = get_knowledge_chunks()
    uploaded_files = st.sidebar.file_uploader(
        tr("upload_label"),
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
    )
    uploaded_chunks = build_chunks_from_uploaded_files(uploaded_files)
    all_chunks = knowledge_chunks + uploaded_chunks

    st.sidebar.caption(f"{tr('built_in_chunks')}: {len(knowledge_chunks)}")
    st.sidebar.caption(f"{tr('uploaded_chunks')}: {len(uploaded_chunks)}")
    if uploaded_files:
        st.sidebar.write(f"{tr('uploaded_files')}:")
        for uploaded_file in uploaded_files:
            st.sidebar.write(f"- {uploaded_file.name}")

    mode_labels_ui = [tr("mode_cfa_pro"), tr("mode_general")]
    mode_pick = st.sidebar.radio(tr("assistant_mode"), mode_labels_ui, index=0)
    mode = "CFA Pro" if mode_pick == tr("mode_cfa_pro") else "General"

    function_keys = list(PROMPTS.keys())
    function_label_map = {i18n.function_label(lang, key): key for key in function_keys}
    function_display = st.sidebar.selectbox(tr("select_function"), list(function_label_map.keys()), index=0)
    function = function_label_map[function_display]
    st.sidebar.write(f"**{tr('selected_function')}:** {function_display}")
    st.sidebar.write(f"**{tr('current_mode')}:** {mode_pick}")

    tab_assistant, tab_events, tab_quiz = st.tabs([tr("tab_assistant"), tr("tab_events"), tr("tab_quiz")])

    with tab_assistant:
        st.markdown(f"<div class='module-header'>{tr('module_assistant')}</div>", unsafe_allow_html=True)

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            render_status_card(tr("domain"), tr("domain_cfa") if mode == "CFA Pro" else tr("domain_general"))
        with s2:
            render_status_card(tr("grounding"), tr("grounding_first") if mode == "CFA Pro" else tr("grounding_optional"))
        with s3:
            render_status_card(tr("builtin_chunks_label"), str(len(knowledge_chunks)))
        with s4:
            render_status_card(tr("upload_chunks_label"), str(len(uploaded_chunks)))

        st.markdown(f"### {tr('ask_question')}")
        user_input = st.text_area(
            tr("question_label"),
            placeholder=tr("question_placeholder"),
            height=120,
        )
        submit_button = st.button(tr("btn_submit"), use_container_width=True)

        if submit_button:
            if not user_input.strip():
                st.warning(tr("please_enter_question"))
            else:
                st.markdown(f"### {tr('your_question')}")
                st.markdown(f"<div class='answer-frame'>{user_input}</div>", unsafe_allow_html=True)

                direct_events_answer = False
                retrieved_chunks = []
                confidence = "N/A"
                answer = None
                with st.spinner(tr("generating")):
                    if mode == "CFA Pro" and is_events_query(user_input):
                        events_payload = load_cached_payload()
                        if events_payload is None:
                            try:
                                events_payload = get_latest_events_payload()
                            except Exception:
                                events_payload = None

                        if events_payload:
                            snapshot = serialize_payload(events_payload)
                            display_rows = rows_for_events_payload(snapshot, lang, use_ai_enrich=False)
                            answer = build_events_answer_markdown(events_payload, display_rows, lang)
                            confidence = "High"
                            direct_events_answer = True
                            st.session_state["assistant_events_snapshot"] = snapshot
                            st.session_state["assistant_events_snapshot_lang"] = lang
                            st.session_state.pop("assistant_events_ai_markdown", None)
                            st.markdown(
                                f"<div class='answer-frame'><b>{tr('pro_response')}</b> | <b>{tr('mode_label')}:</b> {tr('mode_cfa_pro')} | "
                                f"<b>{tr('confidence')}:</b> High | <b>{tr('official_events')}</b></div>",
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"### {tr('answer')}\n\n{answer}")

                    if not direct_events_answer:
                        st.session_state.pop("assistant_events_snapshot", None)
                        st.session_state.pop("assistant_events_ai_markdown", None)
                        prompt_func = PROMPTS.get(function)
                        prompt = prompt_func(user_input) if callable(prompt_func) else prompt_func
                        retrieved_chunks = retrieve_chunks(user_input, all_chunks, top_k=3)
                        context_text = format_context(retrieved_chunks)
                        confidence = "High" if len(retrieved_chunks) >= 2 else ("Medium" if len(retrieved_chunks) == 1 else "Low")
                        lang_line = i18n.language_instruction(lang)

                        if mode == "CFA Pro" and context_text:
                            prompt = (
                                f"{prompt}\n\n"
                                f"{PRO_MODE_INSTRUCTIONS}\n\n"
                                f"{lang_line}\n\n"
                                "Use the context below when relevant. If the context is insufficient, "
                                "say that the answer is based on general guidance and recommend checking official CFA sources.\n\n"
                                f"--- Retrieved Context ---\n{context_text}\n\n"
                                "When using retrieved context, cite the source labels like [Source 1]."
                            )
                        elif mode == "CFA Pro":
                            prompt = (
                                f"{prompt}\n\n"
                                f"{PRO_MODE_INSTRUCTIONS}\n\n"
                                f"{lang_line}\n\n"
                                "No document context was retrieved. Provide a careful general answer and "
                                "recommend verifying policy/event details on official CFA websites."
                            )
                        else:
                            prompt = (
                                f"{prompt}\n\n"
                                f"{GENERAL_MODE_INSTRUCTIONS}\n\n"
                                f"{lang_line}\n\n"
                                f"Optional context for reference:\n{context_text if context_text else 'No retrieved context.'}"
                            )

                        if prompt:
                            output_area = st.empty()
                            streamed_answer = ""
                            if mode == "CFA Pro":
                                grounded_label = tr("grounded_sources") if retrieved_chunks else tr("no_source_match")
                                st.markdown(
                                    f"<div class='answer-frame'><b>{tr('pro_response')}</b> | <b>{tr('mode_label')}:</b> {tr('mode_cfa_pro')} | "
                                    f"<b>{tr('confidence')}:</b> {confidence} | <b>{grounded_label}</b></div>",
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.markdown(
                                    f"<div class='answer-frame'><b>{tr('gen_response')}</b> | <b>{tr('mode_label')}:</b> {tr('mode_general')}</div>",
                                    unsafe_allow_html=True,
                                )
                            for chunk in query_openai_stream(prompt, user_input):
                                streamed_answer += chunk
                                output_area.markdown(f"### {tr('answer')}\n\n{streamed_answer}")
                            answer = streamed_answer
                        else:
                            answer = "Invalid prompt. Please check your PROMPTS configuration."
                            st.error(answer)

                if answer:
                    st.markdown(f"**{tr('matched_sources')}**")
                    source_labels = [chunk.source for chunk in retrieved_chunks]
                    if direct_events_answer:
                        source_labels = ["official:cfa-society-france-home"]
                    render_source_chips(source_labels, lang)

                    if "history" not in st.session_state:
                        st.session_state.history = []
                    st.session_state.history.append({
                        "mode": mode,
                        "function": function,
                        "question": user_input,
                        "answer": answer,
                        "sources": source_labels,
                        "confidence": confidence,
                    })
                    save_log(function, user_input, answer)

        snap = st.session_state.get("assistant_events_snapshot")
        snap_lang = st.session_state.get("assistant_events_snapshot_lang")
        if snap and snap_lang != lang:
            st.session_state.pop("assistant_events_ai_markdown", None)
            st.session_state["assistant_events_snapshot_lang"] = lang
        if snap:
            st.markdown("---")
            st.caption(tr("assistant_events_ai_optin_caption"))
            if st.button(tr("assistant_events_ai_enrich_btn"), key="assistant_events_ai_enrich_click"):
                with st.spinner(tr("assistant_events_ai_generating")):
                    ep = deserialize_payload(snap)
                    enriched_rows = rows_for_events_payload(snap, lang, use_ai_enrich=True)
                    st.session_state["assistant_events_ai_markdown"] = build_events_answer_markdown(
                        ep, enriched_rows, lang
                    )
                    st.rerun()
            aimd = st.session_state.get("assistant_events_ai_markdown")
            if aimd:
                st.markdown(f"### {tr('assistant_events_ai_heading')}")
                st.caption(tr("events_ai_note"))
                st.markdown(aimd)

        if "history" in st.session_state and st.session_state.history:
            st.write(f"### {tr('chat_history')}")
            for i, record in enumerate(st.session_state.history):
                with st.expander(
                    f"{tr('conversation')} {i+1} | {record.get('mode', 'CFA Pro')} | {tr('confidence')}: {record.get('confidence', 'N/A')}",
                    expanded=(i == len(st.session_state.history) - 1),
                ):
                    st.markdown(
                        f"<div class='answer-frame'><b>{tr('function')}:</b> {record['function']}</div>",
                        unsafe_allow_html=True,
                    )
                    st.write(f"**{tr('question')}:** {record['question']}")
                    st.write(f"**{tr('answer')}:** {record['answer']}")
                    st.write(f"**{tr('sources')}:**")
                    render_source_chips(record.get("sources", []), lang)

    with tab_events:
        st.markdown(f"<div class='module-header'>{tr('module_events')}</div>", unsafe_allow_html=True)
        col_sync, col_hint = st.columns([1, 2])
        with col_sync:
            refresh = st.button(tr("events_refresh"), use_container_width=True)
        with col_hint:
            st.caption(f"{tr('events_source_caption')}: https://www.cfasociety.org/france/home")

        payload = None
        if refresh:
            try:
                get_latest_events_payload.clear()
                payload = get_latest_events_payload()
                st.success(tr("events_refreshed"))
            except Exception as e:
                st.warning(f"{tr('events_refresh_fail')} ({e})")

        if payload is None:
            try:
                payload = get_latest_events_payload()
            except Exception:
                payload = load_cached_payload()

        if payload is None:
            st.error(tr("events_no_data"))
        else:
            snapshot = serialize_payload(payload)
            st.session_state.setdefault("events_use_ai_enrich", False)
            b1, b2 = st.columns(2)
            with b1:
                if st.button(tr("events_show_raw"), use_container_width=True):
                    st.session_state["events_use_ai_enrich"] = False
                    st.rerun()
            with b2:
                if st.button(tr("events_ai_enrich_btn"), use_container_width=True):
                    st.session_state["events_use_ai_enrich"] = True
                    st.rerun()
            use_ai = st.session_state.get("events_use_ai_enrich", False)
            display_rows = rows_for_events_payload(snapshot, lang, use_ai_enrich=use_ai)
            st.caption(tr("events_ai_note") if use_ai else tr("events_raw_note"))
            st.write(f"**{tr('last_synced')}:** {payload.synced_at}")
            st.write(f"**{tr('official_source')}:** {payload.source_url}")

            st.markdown(f"### {tr('upcoming_events')}")
            events_ui = display_rows.get("events", [])
            if events_ui:
                for event in events_ui:
                    hl = event.get("highlights") or []
                    highlights_block = ""
                    if hl:
                        highlights_html = "".join([f"<li>{highlight}</li>" for highlight in hl])
                        highlights_block = f"<b>{tr('highlights')}:</b><ul>{highlights_html}</ul>"
                    st.markdown(
                        f"<div class='answer-frame'><b>{event.get('title', '')}</b><br/>"
                        f"<b>{tr('schedule')}:</b> {event.get('schedule', '')}<br/>"
                        f"<b>{tr('location')}:</b> {event.get('location', '')}<br/>"
                        f"<b>{tr('speaker')}:</b> {event.get('speaker', '')}<br/>"
                        f"{highlights_block}"
                        f"<a href=\"{event.get('source_url', payload.source_url)}\" target=\"_blank\">{tr('official_page')}</a></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption(tr("no_events"))

            st.markdown(f"### {tr('latest_updates')}")
            updates_ui = display_rows.get("updates", [])
            if updates_ui:
                for update in updates_ui:
                    st.markdown(
                        f"<div class='answer-frame'><b>{update.get('title', '')}</b><br/>{update.get('summary', '')}<br/>"
                        f"<a href=\"{update.get('source_url', payload.source_url)}\" target=\"_blank\">{tr('official_page')}</a></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption(tr("no_updates"))

    with tab_quiz:
        st.markdown(f"<div class='module-header'>{tr('module_quiz')}</div>", unsafe_allow_html=True)
        questions = load_questions()
        if not questions:
            st.error(tr("quiz_no_questions"))
            st.info(tr("quiz_placeholder"))
        else:
            st.caption(tr("quiz_intro"))
            if st.button(tr("quiz_reset_attempt")):
                for q in questions:
                    key = f"quiz_form_{q.id}"
                    if key in st.session_state:
                        del st.session_state[key]
                if "quiz_last_graded" in st.session_state:
                    del st.session_state["quiz_last_graded"]
                for k in ("quiz_ai_explain", "quiz_ai_weakness", "quiz_ai_practice"):
                    st.session_state.pop(k, None)
                st.rerun()

            with st.form("cfa_quiz_form"):
                for i, q in enumerate(questions):
                    st.markdown(f"**{i + 1}.** · *{tr('quiz_topic_label')}:* {q.topic}")
                    st.markdown(q.stem)
                    st.radio(
                        tr("quiz_pick_one"),
                        options=list(range(len(q.choices))),
                        format_func=lambda idx, _choices=q.choices: _choices[idx],
                        key=f"quiz_form_{q.id}",
                        label_visibility="collapsed",
                    )
                submitted = st.form_submit_button(tr("quiz_submit_grading"))

            if submitted:
                picked: dict = {}
                for q in questions:
                    val = st.session_state.get(f"quiz_form_{q.id}")
                    picked[q.id] = int(val) if val is not None else -1
                correct_n, details = grade(questions, picked)
                st.session_state["quiz_last_graded"] = {
                    "correct": correct_n,
                    "total": len(questions),
                    "details": details,
                }
                for k in ("quiz_ai_explain", "quiz_ai_weakness", "quiz_ai_practice"):
                    st.session_state.pop(k, None)

            graded = st.session_state.get("quiz_last_graded")
            if graded:
                st.success(
                    tr("quiz_score_result").format(correct=graded["correct"], total=graded["total"])
                )
                for q, picked_idx, ok in graded["details"]:
                    status = tr("quiz_correct") if ok else tr("quiz_incorrect")
                    st.markdown(f"**{status}** — *{q.topic}*")
                    st.caption(q.stem)
                    if not ok and 0 <= picked_idx < len(q.choices):
                        st.caption(f"{tr('quiz_your_answer')}: {q.choices[picked_idx]}")
                    if not ok:
                        st.caption(f"{tr('quiz_key_answer')}: {q.choices[q.correct_index]}")
                    st.markdown(f"*{tr('quiz_explanation')}:* {q.explanation}")
                    st.markdown("---")

                st.markdown(f"### {tr('quiz_ai_section')}")
                st.caption(tr("quiz_ai_opt_in_note"))
                qa1, qa2, qa3 = st.columns(3)
                with qa1:
                    go_explain = st.button(tr("quiz_btn_ai_explain"), use_container_width=True, key="quiz_ai_btn_explain")
                with qa2:
                    go_weak = st.button(tr("quiz_btn_ai_weakness"), use_container_width=True, key="quiz_ai_btn_weak")
                with qa3:
                    go_drill = st.button(tr("quiz_btn_ai_practice"), use_container_width=True, key="quiz_ai_btn_drill")

                details = graded["details"]
                wrong_n = sum(1 for _, _, ok in details if not ok)
                if go_explain:
                    with st.spinner(tr("quiz_ai_generating")):
                        out = explain_all_questions(client, lang, details)
                        if out:
                            st.session_state["quiz_ai_explain"] = out
                        else:
                            st.error(tr("quiz_ai_error"))
                if go_weak:
                    if wrong_n == 0:
                        st.info(tr("quiz_ai_no_wrongs"))
                    else:
                        with st.spinner(tr("quiz_ai_generating")):
                            out = analyze_wrong_items(client, lang, details)
                            if out:
                                st.session_state["quiz_ai_weakness"] = out
                            else:
                                st.error(tr("quiz_ai_error"))
                if go_drill:
                    if wrong_n == 0:
                        st.info(tr("quiz_ai_no_wrongs"))
                    else:
                        with st.spinner(tr("quiz_ai_generating")):
                            out = generate_practice_from_wrong(client, lang, details)
                            if out:
                                st.session_state["quiz_ai_practice"] = out
                            else:
                                st.error(tr("quiz_ai_error"))

                ex = st.session_state.get("quiz_ai_explain")
                if ex:
                    st.markdown(f"**{tr('quiz_ai_explain_heading')}**")
                    st.markdown(ex)
                wk = st.session_state.get("quiz_ai_weakness")
                if wk:
                    st.markdown(f"**{tr('quiz_ai_weakness_heading')}**")
                    st.markdown(wk)
                pr = st.session_state.get("quiz_ai_practice")
                if pr:
                    st.markdown(f"**{tr('quiz_ai_practice_heading')}**")
                    st.markdown(pr)


if __name__ == "__main__":
    main()

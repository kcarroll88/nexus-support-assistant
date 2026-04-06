import streamlit as st
import os
import re
import html as _html
from rag import load_documents, chunk_documents, store_chunks, ask, collection

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus Support Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

/* ── Reset & globals ──────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ── App background ───────────────────── */
.stApp {
    background-color: #EEF2FF !important;
    background-image:
        radial-gradient(ellipse 70% 55% at 8% -5%,  rgba(99,102,241,0.13) 0%, transparent 65%),
        radial-gradient(ellipse 55% 45% at 95% 105%, rgba(59,130,246,0.11) 0%, transparent 65%),
        url("data:image/svg+xml,%3Csvg width='36' height='36' viewBox='0 0 36 36' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='18' cy='18' r='1.4' fill='%232563EB' fill-opacity='0.035'/%3E%3C/svg%3E") !important;
    background-attachment: fixed !important;
}

/* ── Hide Streamlit chrome ────────────── */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton { display: none !important; }

/* Push content up since header is gone */
.stApp > div:first-child { padding-top: 0 !important; }
.main .block-container { padding-top: 2.5rem !important; }

/* ── Main content block ───────────────── */
.block-container {
    padding-top: 2.5rem   !important;
    padding-bottom: 4rem  !important;
    padding-left: 2.5rem  !important;
    padding-right: 2.5rem !important;
    max-width: 960px      !important;
}

/* ── Sidebar ──────────────────────────── */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.52) !important;
    backdrop-filter: blur(28px) saturate(200%) !important;
    -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
    border-right: 1px solid rgba(255,255,255,0.78) !important;
    box-shadow: 4px 0 36px rgba(37,99,235,0.07) !important;
}
section[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
    padding-top: 1.75rem !important;
}

/* ── Typography ───────────────────────── */
h1,h2,h3,h4,h5,h6 {
    font-family: 'Inter', sans-serif !important;
    color: #0F172A !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
}

/* ── Buttons (quick-question pills) ────── */
.stButton > button {
    background: rgba(255,255,255,0.62) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(37,99,235,0.17) !important;
    color: #1D4ED8 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.52rem 0.9rem !important;
    width: 100% !important;
    text-align: left !important;
    line-height: 1.45 !important;
    transition: all 0.18s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 8px rgba(37,99,235,0.06) !important;
}
.stButton > button:hover {
    background: rgba(37,99,235,0.07) !important;
    border-color: rgba(37,99,235,0.33) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 18px rgba(37,99,235,0.13) !important;
    color: #1E40AF !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 1px 4px rgba(37,99,235,0.09) !important;
}

/* ── Sidebar rebuild button (override) ─── */
section[data-testid="stSidebar"] .stButton > button {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    background: transparent !important;
    border: 1px solid rgba(100,116,139,0.22) !important;
    color: #64748B !important;
    font-size: 0.78rem !important;
    padding: 0.42rem 0.9rem !important;
    border-radius: 8px !important;
    width: auto !important;
    text-align: center !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(37,99,235,0.05) !important;
    border-color: rgba(37,99,235,0.28) !important;
    color: #2563EB !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Text input ───────────────────────── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.78) !important;
    backdrop-filter: blur(14px) !important;
    border: 1.5px solid rgba(37,99,235,0.17) !important;
    border-radius: 13px !important;
    padding: 0.82rem 1.2rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    color: #0F172A !important;
    box-shadow: 0 2px 14px rgba(37,99,235,0.06) !important;
    transition: all 0.18s cubic-bezier(0.4,0,0.2,1) !important;
    height: auto !important;
}
.stTextInput > div > div > input:focus,
.stTextInput > div > div > input:focus-visible {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.10), 0 2px 14px rgba(37,99,235,0.08) !important;
    background: rgba(255,255,255,0.94) !important;
    outline: none !important;
}
/* Kill Streamlit's default pink/red focus ring on the wrapper div */
.stTextInput > div:focus-within,
.stTextInput > div > div:focus-within {
    box-shadow: none !important;
    border-color: transparent !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: #94A3B8 !important;
    font-style: normal !important;
}

/* ── Spinner ──────────────────────────── */
div[data-testid="stSpinner"] > div {
    border-top-color: #2563EB !important;
}

/* ══════════════════════════════════════
   KEYFRAMES
══════════════════════════════════════ */
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseDot {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.5; transform:scale(.78); }
}

/* ══════════════════════════════════════
   CUSTOM COMPONENTS
══════════════════════════════════════ */

/* ── Page header ──────────────────────── */
.nxa-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 2rem;
    animation: fadeInDown 0.45s cubic-bezier(0.4,0,0.2,1) both;
}
.nxa-header-icon {
    width: 54px; height: 54px;
    flex-shrink: 0;
    background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 22px rgba(37,99,235,0.30);
}
.nxa-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.035em;
    line-height: 1.15;
    margin: 0 0 5px;
}
.nxa-subtitle {
    font-size: 0.875rem;
    color: #64748B;
    font-weight: 400;
    margin: 0;
    line-height: 1.55;
}

/* ── Sidebar components ───────────────── */
.nxa-sb-heading {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 14px;
}
.nxa-sb-heading-text {
    font-size: 0.71rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin: 0;
}
.nxa-doc-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    background: rgba(255,255,255,0.42);
    border: 1px solid rgba(37,99,235,0.09);
    border-radius: 9px;
    margin-bottom: 6px;
    transition: background 0.16s, border-color 0.16s;
}
.nxa-doc-item:hover {
    background: rgba(255,255,255,0.72);
    border-color: rgba(37,99,235,0.2);
}
.nxa-doc-icon {
    flex-shrink: 0;
    opacity: 0.55;
}
.nxa-doc-name {
    font-size: 0.78rem;
    font-weight: 500;
    color: #334155;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.nxa-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.20);
    color: #047857;
    border-radius: 20px;
    padding: 4px 11px;
    font-size: 0.73rem;
    font-weight: 500;
    margin-top: 10px;
}
.nxa-status-dot {
    width: 6px; height: 6px;
    background: #10B981;
    border-radius: 50%;
    flex-shrink: 0;
    animation: pulseDot 2.4s ease-in-out infinite;
}
.nxa-sb-divider {
    border: none;
    border-top: 1px solid rgba(37,99,235,0.08);
    margin: 18px 0 14px;
}

/* ── Section labels ───────────────────── */
.nxa-label {
    font-size: 0.71rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin: 0 0 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── Search row ───────────────────────── */
.nxa-search-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin: 6px 0 8px;
    animation: fadeInDown 0.45s 0.1s both;
}

/* ── Answer card ──────────────────────── */
.nxa-answer-card {
    background: rgba(255,255,255,0.70);
    backdrop-filter: blur(26px) saturate(180%);
    -webkit-backdrop-filter: blur(26px) saturate(180%);
    border: 1px solid rgba(255,255,255,0.85);
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow:
        0 1px 2px rgba(0,0,0,0.03),
        0 4px 18px rgba(37,99,235,0.07),
        0 14px 44px rgba(37,99,235,0.04);
    animation: fadeInUp 0.4s cubic-bezier(0.4,0,0.2,1) both;
}
.nxa-answer-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 14px;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(37,99,235,0.07);
}
.nxa-answer-badge {
    font-size: 0.71rem;
    font-weight: 600;
    color: #2563EB;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin: 0;
}
.nxa-answer-body {
    font-size: 0.925rem;
    line-height: 1.82;
    color: #1E293B;
}
.nxa-answer-body p  { margin: 0 0 0.75em; }
.nxa-answer-body p:last-child { margin-bottom: 0; }
.nxa-answer-body strong { font-weight: 600; color: #0F172A; }
.nxa-answer-body em { font-style: italic; }
.nxa-answer-body ul, .nxa-answer-body ol { padding-left: 1.45em; margin: 0.4em 0 0.75em; }
.nxa-answer-body li { margin-bottom: 0.28em; }
.nxa-answer-body code {
    background: rgba(37,99,235,0.07);
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 0.875em;
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    color: #1D4ED8;
}
.nxa-answer-body h3,.nxa-answer-body h4,.nxa-answer-body h5,.nxa-answer-body h6 {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: #0F172A !important;
    margin: 0.9em 0 0.3em !important;
    letter-spacing: -0.01em !important;
}

/* ── Source cards ─────────────────────── */
.nxa-source-card {
    display: flex;
    align-items: center;
    gap: 14px;
    background: rgba(255,255,255,0.58);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(37,99,235,0.09);
    border-radius: 13px;
    padding: 12px 16px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 2px 10px rgba(37,99,235,0.04);
    animation: fadeInUp 0.4s cubic-bezier(0.4,0,0.2,1) both;
}
.nxa-source-icon-wrap {
    width: 38px; height: 38px;
    background: rgba(37,99,235,0.07);
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.nxa-source-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1E293B;
    margin: 0 0 2px;
}
.nxa-source-meta {
    font-size: 0.74rem;
    color: #94A3B8;
    font-weight: 400;
    margin: 0;
}

/* ── Misc utilities ───────────────────── */
.nxa-spacer    { height: 16px; }
.nxa-spacer-sm { height: 8px; }
</style>
""",
    unsafe_allow_html=True,
)

# ── SVG icon helpers ──────────────────────────────────────────────────────────

def _svg(paths, size=16, color="currentColor", sw=1.5, extra_attrs=""):
    if isinstance(paths, str):
        paths = [paths]
    path_tags = "".join(f'<path d="{p}"/>' for p in paths)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra_attrs}>'
        f"{path_tags}</svg>"
    )

# Icon paths (Heroicons outline)
_P_DOC    = "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
_P_BOOK   = "M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
_P_SPARK  = "M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z"
_P_SEARCH = "M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 15.803 7.5 7.5 0 0016.05 15.803z"
_P_LINK   = "M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244"
_P_REFRESH= "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
_P_BOLT   = "M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"

NEXUS_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" '
    'fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M6 4v16l12-16v16"/>'
    "</svg>"
)

# ── Markdown → HTML helper ────────────────────────────────────────────────────

def md_to_html(text: str) -> str:
    """Convert a subset of markdown to HTML for display in the answer card."""
    # Escape HTML entities first so user content can't inject tags
    text = _html.escape(text)

    # Process line by line first to handle headings and lists correctly
    lines = text.split("\n")
    result: list[str] = []
    in_ul = in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            result.append("</ul>")
            in_ul = False
        if in_ol:
            result.append("</ol>")
            in_ol = False

    def inline(s: str) -> str:
        """Apply inline markdown (bold, italic, code) to a string."""
        # Bold — must come before italic
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        # Italic — single * not adjacent to another *
        s = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", s)
        # Inline code
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        return s

    for raw in lines:
        stripped = raw.strip()

        # ATX headings  (### Heading)
        h_match = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if h_match:
            close_lists()
            level = min(len(h_match.group(1)) + 2, 6)  # h3-h6 to stay subordinate
            result.append(f"<h{level}>{inline(h_match.group(2))}</h{level}>")
            continue

        # Unordered list item
        if re.match(r"^[-*]\s+", stripped):
            if not in_ul:
                if in_ol:
                    result.append("</ol>")
                    in_ol = False
                result.append("<ul>")
                in_ul = True
            content = re.sub(r"^[-*]\s+", "", stripped)
            result.append(f"<li>{inline(content)}</li>")
            continue

        # Ordered list item
        if re.match(r"^\d+\.\s+", stripped):
            if not in_ol:
                if in_ul:
                    result.append("</ul>")
                    in_ul = False
                result.append("<ol>")
                in_ol = True
            content = re.sub(r"^\d+\.\s+", "", stripped)
            result.append(f"<li>{inline(content)}</li>")
            continue

        # Blank line — close open lists, skip
        if not stripped:
            close_lists()
            continue

        # Normal paragraph line
        close_lists()
        result.append(f"<p>{inline(stripped)}</p>")

    close_lists()
    return "\n".join(result)

# ── Initialise knowledge base ─────────────────────────────────────────────────

@st.cache_resource
def initialize():
    if collection.count() == 0:
        with st.spinner("Building knowledge base index…"):
            docs = load_documents()
            chunks = chunk_documents(docs)
            store_chunks(chunks)
    return True

initialize()

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="nxa-header">
  <div class="nxa-header-icon">{NEXUS_ICON_SVG}</div>
  <div>
    <p class="nxa-title">Nexus Support Assistant</p>
    <p class="nxa-subtitle">
      Instant answers from your knowledge base &mdash;
      powered by semantic search &amp; Claude AI
    </p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Heading
    st.markdown(
        f"""
<div class="nxa-sb-heading">
  {_svg(_P_BOOK, size=15, color="#64748B")}
  <p class="nxa-sb-heading-text">Knowledge Base</p>
</div>
""",
        unsafe_allow_html=True,
    )

    # Document list
    doc_files = [f for f in os.listdir("docs") if f.endswith(".pdf")]
    for doc in doc_files:
        display = doc.replace(".pdf", "").replace("-", " ")
        st.markdown(
            f"""
<div class="nxa-doc-item">
  <span class="nxa-doc-icon">{_svg(_P_DOC, size=15, color="#2563EB")}</span>
  <p class="nxa-doc-name" title="{_html.escape(doc)}">{_html.escape(display)}</p>
</div>
""",
            unsafe_allow_html=True,
        )

    # Status pill
    st.markdown(
        f"""
<div class="nxa-status-pill">
  <div class="nxa-status-dot"></div>
  {collection.count()} chunks indexed
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="nxa-sb-divider">', unsafe_allow_html=True)

    # Rebuild button  (st.button labels are plain text — no HTML)
    if st.button("Rebuild Index", key="rebuild"):
        import shutil
        shutil.rmtree("chroma_db", ignore_errors=True)
        st.cache_resource.clear()
        st.rerun()

# ── Quick-question buttons ────────────────────────────────────────────────────
st.markdown(
    '<p class="nxa-label">Quick Questions</p>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("How do I reset a password?"):
        st.session_state.query = "How do I reset a password?"
with col2:
    if st.button("What's in the latest release?"):
        st.session_state.query = "What's in the latest release?"
with col3:
    if st.button("How do I handle a refund request?"):
        st.session_state.query = "How do I handle a refund request?"

# ── Search input ──────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="nxa-search-label">
  {_svg(_P_SEARCH, size=16, color="#374151")}
  Ask a support question
</div>
""",
    unsafe_allow_html=True,
)

query = st.text_input(
    "query",
    value=st.session_state.get("query", ""),
    placeholder="e.g. Customer cannot log in — what are the steps?",
    label_visibility="collapsed",
)

# ── Results ───────────────────────────────────────────────────────────────────
if query:
    with st.spinner("Searching knowledge base…"):
        answer, sources = ask(query)

    # Answer card
    st.markdown(
        f"""
<div class="nxa-answer-card">
  <div class="nxa-answer-header">
    {_svg(_P_SPARK, size=16, color="#2563EB")}
    <p class="nxa-answer-badge">Answer</p>
  </div>
  <div class="nxa-answer-body">{md_to_html(answer)}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Source documents
    st.markdown(
        f"""<p class="nxa-label">
  {_svg(_P_LINK, size=13, color="#94A3B8")}
  Source Documents
</p>""",
        unsafe_allow_html=True,
    )

    for i, source in enumerate(sources):
        display = source.replace(".pdf", "").replace("-", " ")
        delay = f"animation-delay:{i * 0.07:.2f}s"
        st.markdown(
            f"""
<div class="nxa-source-card" style="{delay}">
  <div class="nxa-source-icon-wrap">
    {_svg(_P_DOC, size=18, color="#2563EB")}
  </div>
  <div>
    <p class="nxa-source-name">{_html.escape(display)}</p>
    <p class="nxa-source-meta">PDF &mdash; Knowledge Base Document</p>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

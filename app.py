import sys
import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from html import escape

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from ai.interpreter import interpret_mood, MoodProfile
from ai.retriever import fetch_candidates, CandidateSong
from ai.scorer import rank_candidates, ScoredSong, score_candidate
from audiodb import fetch_mostloved
from ai.explainer import explain_recommendations
from ai.enricher import enrich_candidates
from ai.guardrails import validate_input
from ai.logger import (
    log_run_start, log_validation_fail, log_profile,
    log_retrieval, log_ranked, log_explanation, log_error, logger,
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Moodwave",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Design System ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400&family=DM+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    background-color: #0A0A0F !important;
    color: #F0EAD6;
    font-family: 'DM Sans', sans-serif;
}
.main { background-color: #0A0A0F !important; }
.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 660px !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Typography ── */
.mw-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #C9A84C;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.mw-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 5vw, 3.4rem);
    font-weight: 700;
    color: #F0EAD6;
    line-height: 1.08;
    letter-spacing: -0.025em;
    margin-bottom: 0.4rem;
}
.mw-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 300;
    color: #7A7A8C;
    margin-bottom: 2.8rem;
    line-height: 1.5;
}

/* ── Equalizer animation (Lottie fallback) ── */
.eq-fallback {
    display: flex;
    align-items: flex-end;
    gap: 5px;
    height: 52px;
    margin-bottom: 2.2rem;
}
.eq-bar {
    width: 5px;
    border-radius: 3px 3px 0 0;
    background: #C9A84C;
    animation: eq-bounce 1.2s ease-in-out infinite;
    opacity: 0.85;
}
.eq-bar:nth-child(1) { height: 28px; animation-delay: 0s; }
.eq-bar:nth-child(2) { height: 44px; animation-delay: 0.15s; }
.eq-bar:nth-child(3) { height: 36px; animation-delay: 0.3s; }
.eq-bar:nth-child(4) { height: 52px; animation-delay: 0.1s; }
.eq-bar:nth-child(5) { height: 24px; animation-delay: 0.4s; }
.eq-bar:nth-child(6) { height: 40px; animation-delay: 0.25s; }
.eq-bar:nth-child(7) { height: 32px; animation-delay: 0.5s; }
@keyframes eq-bounce {
    0%, 100% { transform: scaleY(0.4); }
    50%       { transform: scaleY(1.0); }
}

/* ── Text area ── */
.stTextArea > div > div > textarea {
    background: #11111A !important;
    border: 1px solid #22222F !important;
    border-radius: 14px !important;
    color: #F0EAD6 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 300 !important;
    line-height: 1.6 !important;
    padding: 1.1rem 1.3rem !important;
    resize: none !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
    caret-color: #C9A84C !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 3px rgba(201, 168, 76, 0.10) !important;
    outline: none !important;
}
.stTextArea > div > div > textarea::placeholder {
    color: #3A3A4A !important;
    font-style: italic !important;
}

/* ── Submit button ── */
.stButton { margin-top: 0.75rem; }
.stButton > button {
    background: #C9A84C !important;
    color: #0A0A0F !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 0.7rem 2.2rem !important;
    transition: opacity 0.2s ease, transform 0.15s ease !important;
    cursor: pointer !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* ── Alerts ── */
.stAlert {
    background: #1A1410 !important;
    border: 1px solid #3A2A10 !important;
    border-radius: 10px !important;
    color: #C9A84C !important;
}

/* ── Echo card ── */
.mw-echo {
    background: #11111A;
    border: 1px solid #1E1E2A;
    border-left: 3px solid #C9A84C;
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-top: 1.8rem;
}
.mw-echo-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #C9A84C;
    letter-spacing: 0.20em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.mw-echo-text {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 300;
    color: #D0CAB8;
    line-height: 1.6;
}

/* ── What I Heard card ── */
.mw-profile {
    background: #0D0D16;
    border: 1px solid #1E1E2A;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-top: 1.4rem;
}
.mw-profile-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #C9A84C;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 1.1rem;
}
.mw-profile-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem 1.5rem;
    margin-bottom: 1rem;
}
.mw-attr {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}
.mw-attr-key {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    color: #4A4A5A;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}
.mw-attr-val {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.92rem;
    font-weight: 400;
    color: #F0EAD6;
}
.mw-bar-track {
    height: 4px;
    background: #1E1E2A;
    border-radius: 2px;
    margin-top: 0.3rem;
    overflow: hidden;
}
.mw-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #7A5C20, #C9A84C);
}
.mw-keywords {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.8rem;
}
.mw-chip {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #C9A84C;
    background: rgba(201, 168, 76, 0.08);
    border: 1px solid rgba(201, 168, 76, 0.2);
    border-radius: 20px;
    padding: 0.25rem 0.7rem;
    letter-spacing: 0.06em;
}
.mw-next-hint {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #2E2E3A;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 1.1rem;
}

/* ── Candidates list ── */
.mw-candidates {
    background: #0D0D16;
    border: 1px solid #1E1E2A;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-top: 1.4rem;
}
.mw-candidates-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #C9A84C;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.mw-song-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: 0.55rem 0;
    border-bottom: 1px solid #14141E;
    gap: 1rem;
}
.mw-song-row:last-of-type { border-bottom: none; }
.mw-song-info { flex: 1; min-width: 0; }
.mw-song-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.92rem;
    font-weight: 400;
    color: #F0EAD6;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.mw-song-artist {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 300;
    color: #5A5A6A;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.mw-song-dur {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #3A3A4A;
    flex-shrink: 0;
}
.mw-count-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #7A7A8C;
    margin-bottom: 0.8rem;
    letter-spacing: 0.08em;
}

/* ── Ranked results ── */
.mw-ranked-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #C9A84C;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-top: 1.4rem;
    margin-bottom: 0.6rem;
}
.mw-ranked-row {
    display: grid;
    grid-template-columns: 1.4rem 1fr auto;
    align-items: start;
    gap: 0.6rem 0.8rem;
    padding: 0.75rem 1rem;
    margin-bottom: 0.25rem;
    background: #0D0D16;
    border: 1px solid #1A1A24;
    border-radius: 10px;
}
.mw-ranked-row--rich { display: flex; align-items: center; gap: 12px; }
.mw-thumb { width: 56px; height: 56px; border-radius: 6px; object-fit: cover; flex-shrink: 0; }
.mw-thumb-placeholder { width: 56px; height: 56px; border-radius: 6px; background: #1a1a1a; flex-shrink: 0; }
.mw-theme-badge { font-size: 11px; background: #2a2a1a; color: #b8a96a; border-radius: 4px; padding: 2px 6px; margin-top: 4px; display: inline-block; }
.mw-yt-link { font-size: 12px; color: #888; text-decoration: none; margin-top: 4px; display: inline-block; }
.mw-yt-link:hover { color: #b8a96a; }
.mw-rank-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #C9A84C;
    padding-top: 0.1rem;
}
.mw-ranked-info { min-width: 0; }
.mw-ranked-title-text {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 400;
    color: #F0EAD6;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.mw-ranked-artist {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 300;
    color: #5A5A6A;
    margin-top: 0.1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.mw-ranked-reasons {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    color: #3A3A4A;
    margin-top: 0.25rem;
    line-height: 1.5;
}
.mw-score-block {
    text-align: right;
    flex-shrink: 0;
}
.mw-score-val {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #C9A84C;
    font-weight: 500;
}
.mw-score-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    color: #3A3A4A;
    letter-spacing: 0.08em;
}

/* ── Explanation card ── */
.mw-explain {
    background: #0A0A12;
    border: 1px solid #1E1E2A;
    border-top: 2px solid #C9A84C;
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1.4rem;
}
.mw-explain-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #C9A84C;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.mw-explain-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.08rem;
    font-style: italic;
    color: #D8D2C0;
    line-height: 1.8;
}

/* ── Follow-up section ── */
.mw-followup-header {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #4A4A5A;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 2.8rem;
    margin-bottom: 0.9rem;
    padding-top: 2rem;
    border-top: 1px solid #14141E;
}
</style>
""", unsafe_allow_html=True)


# ── Lottie Loader ─────────────────────────────────────────────────────────────
def _load_lottie_url(url: str):
    try:
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def render_animation():
    lottie_url = "https://lottie.host/4db68bbd-79af-4ce7-987f-9e5b65f93693/LpB2Y5gDm5.json"
    animation = _load_lottie_url(lottie_url)
    if animation:
        try:
            from streamlit_lottie import st_lottie
            st_lottie(animation, height=140, speed=0.75, key="eq_lottie")
            return
        except ImportError:
            pass
    st.markdown("""
    <div class="eq-fallback">
        <div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div>
        <div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div>
        <div class="eq-bar"></div>
    </div>
    """, unsafe_allow_html=True)


# ── Equalizer Loading Animation ───────────────────────────────────────────────
def render_loading_animation(slot):
    html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
(function () {
  const pdoc = window.parent.document;

  const stale = pdoc.getElementById('music-loading-overlay');
  if (stale) stale.remove();
  const staleStyle = pdoc.getElementById('music-loading-style');
  if (staleStyle) staleStyle.remove();

  // ── Inject CSS into parent <head> ────────────────────────────────────────────
  const styleEl = pdoc.createElement('style');
  styleEl.id = 'music-loading-style';
  styleEl.textContent =
    '@keyframes mwEqBounce{0%{transform:scaleY(1)}100%{transform:scaleY(0.167)}}' +
    '@keyframes mwVibePulse{0%,100%{opacity:0.25}50%{opacity:1}}' +
    '#music-loading-overlay .eq-bar{' +
    'width:6px;border-radius:3px;background:#C9A84C;height:48px;' +
    'transform-origin:bottom;' +
    'animation:mwEqBounce 0.8s ease-in-out infinite alternate;}' +
    '#music-loading-overlay .vibe-text{' +
    'font-family:"DM Mono","Courier New",monospace;font-size:0.68rem;' +
    'color:#C9A84C;letter-spacing:0.30em;text-transform:uppercase;' +
    'margin-top:24px;user-select:none;' +
    'animation:mwVibePulse 2.5s ease-in-out infinite!important;}';
  pdoc.head.appendChild(styleEl);

  // ── Build overlay in parent <body> ───────────────────────────────────────────
  const overlay = pdoc.createElement('div');
  overlay.id = 'music-loading-overlay';
  overlay.style.cssText =
    'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:9999;' +
    'background:rgba(10,10,15,0.88);' +
    'backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);' +
    'display:flex;flex-direction:column;align-items:center;justify-content:center;';

  const barsRow = pdoc.createElement('div');
  barsRow.style.cssText = 'display:flex;align-items:flex-end;gap:8px;';
  [0, 0.15, 0.3, 0.45, 0.6].forEach(delay => {
    const bar = pdoc.createElement('div');
    bar.className = 'eq-bar';
    bar.style.animationDelay = delay + 's';
    barsRow.appendChild(bar);
  });
  overlay.appendChild(barsRow);

  const textEl = pdoc.createElement('div');
  textEl.className = 'vibe-text';
  textEl.textContent = 'Reading your vibe…';
  textEl.style.animation = 'mwVibePulse 2.5s ease-in-out infinite';
  overlay.appendChild(textEl);

  pdoc.body.appendChild(overlay);

  // ── Cleanup: primary — fires when Streamlit replaces iframe content ──────────
  function cleanup() {
    try {
      pdoc.getElementById('music-loading-overlay')?.remove();
      pdoc.getElementById('music-loading-style')?.remove();
    } catch(e) {}
  }
  window.addEventListener('unload', cleanup);
  window.addEventListener('pagehide', cleanup);

  // ── Cleanup: fallback — fires if Streamlit removes the iframe element ─────────
  const iframeEl = window.frameElement;
  const observer = new MutationObserver(() => {
    if (!pdoc.contains(iframeEl)) {
      overlay.remove();
      styleEl.remove();
      observer.disconnect();
    }
  });
  observer.observe(pdoc.body, { childList: true, subtree: true });
})();
</script>
</body>
</html>"""
    with slot:
        components.html(html, height=1)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _bar(value: float) -> str:
    pct = int(value * 100)
    return f'<div class="mw-bar-track"><div class="mw-bar-fill" style="width:{pct}%"></div></div>'


def render_profile_card(profile: MoodProfile):
    acoustic_label = "Yes" if profile.acoustic else "No"
    keywords_html = "".join(
        f'<span class="mw-chip">{kw}</span>' for kw in profile.search_keywords
    )
    st.markdown(f"""
    <div class="mw-profile">
        <div class="mw-profile-title">What I heard</div>
        <div class="mw-profile-grid">
            <div class="mw-attr">
                <span class="mw-attr-key">Genre</span>
                <span class="mw-attr-val">{profile.genre.title()}</span>
            </div>
            <div class="mw-attr">
                <span class="mw-attr-key">Mood</span>
                <span class="mw-attr-val">{profile.mood.title()}</span>
            </div>
            <div class="mw-attr">
                <span class="mw-attr-key">Energy</span>
                <span class="mw-attr-val">{profile.energy:.0%}</span>
                {_bar(profile.energy)}
            </div>
            <div class="mw-attr">
                <span class="mw-attr-key">Valence</span>
                <span class="mw-attr-val">{profile.valence:.0%}</span>
                {_bar(profile.valence)}
            </div>
            <div class="mw-attr">
                <span class="mw-attr-key">Tempo</span>
                <span class="mw-attr-val">{profile.tempo.title()}</span>
            </div>
            <div class="mw-attr">
                <span class="mw-attr-key">Acoustic</span>
                <span class="mw-attr-val">{acoustic_label}</span>
            </div>
        </div>
        <div class="mw-keywords">{keywords_html}</div>
        <div class="mw-next-hint">↳ Searching catalog — Chapter 3</div>
    </div>
    """, unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _fmt_duration(ms: int | None) -> str:
    if not ms:
        return "—"
    total_s = ms // 1000
    return f"{total_s // 60}:{total_s % 60:02d}"


def _split_reasons(reasons: list[str]) -> tuple[list[str], list[str]]:
    """Separate user-facing score reasons from debug/diagnostic lines."""
    debug, clean = [], []
    for r in reasons:
        if (
            r.startswith("[MB")
            or "not in MB data" in r
            or r.lower().startswith("keyword")
        ):
            debug.append(r)
        else:
            clean.append(r)
    return clean, debug


def render_ranked_card(ranked: list[ScoredSong]):
    st.markdown(
        '<div class="mw-ranked-title">Top picks — scored &amp; ranked</div>',
        unsafe_allow_html=True,
    )
    for i, s in enumerate(ranked, start=1):
        clean, debug = _split_reasons(s.reasons)
        clean_text = " · ".join(clean) if clean else "—"

        thumb = s.candidate.adb_thumb_url
        thumb_html = (
            f'<img class="mw-thumb" src="{thumb}/small" alt="">'
            if thumb and thumb.startswith("https://")
            else '<div class="mw-thumb-placeholder"></div>'
        )

        theme = s.candidate.adb_theme
        theme_html = (
            f'<span class="mw-theme-badge">{escape(theme)}</span>'
            if theme else ""
        )

        yt = s.candidate.adb_youtube_url
        yt_html = (
            f'<a class="mw-yt-link" href="{yt}" target="_blank" rel="noopener">▶ Watch</a>'
            if yt and yt.startswith("https://www.youtube.com/")
            else ""
        )

        st.markdown(
            f'<div class="mw-ranked-row mw-ranked-row--rich">'
            f'{thumb_html}'
            f'<div class="mw-rank-num">#{i}</div>'
            f'<div class="mw-ranked-info">'
            f'<div class="mw-ranked-title-text">{escape(s.candidate.title)}</div>'
            f'<div class="mw-ranked-artist">{escape(s.candidate.artist)}</div>'
            f'<div class="mw-ranked-reasons">{escape(clean_text)}</div>'
            f'{theme_html}'
            f'{yt_html}'
            f'</div>'
            f'<div class="mw-score-block">'
            f'<div class="mw-score-val">{s.score:.0f}</div>'
            f'<div class="mw-score-label">/ 100</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if debug:
            with st.expander("Scoring details"):
                st.caption(" · ".join(debug))
    st.markdown(
        '<div class="mw-next-hint">↳ AI explanation — Chapter 5</div>',
        unsafe_allow_html=True,
    )


def render_explanation_card(text: str):
    st.markdown(
        f'<div class="mw-explain">'
        f'<div class="mw-explain-label">Why these songs</div>'
        f'<div class="mw-explain-text">{escape(text)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_candidates_card(candidates: list[CandidateSong]):
    rows = [
        '<div class="mw-song-row">'
        '<div class="mw-song-info">'
        f'<div class="mw-song-title">{escape(song.title)}</div>'
        f'<div class="mw-song-artist">{escape(song.artist)}</div>'
        '</div>'
        f'<div class="mw-song-dur">{_fmt_duration(song.duration_ms)}</div>'
        '</div>'
        for song in candidates
    ]
    html = (
        '<div class="mw-candidates">'
        '<div class="mw-candidates-title">Catalog results</div>'
        f'<div class="mw-count-badge">{len(candidates)} songs retrieved from MusicBrainz</div>'
        + "".join(rows)
        + '<div class="mw-next-hint">↳ Scoring & ranking — Chapter 4</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ── Session State Init ────────────────────────────────────────────────────────
for key, default in [
    ("submitted_mood", None),
    ("mood_profile", None),
    ("mood_profile_error", None),
    ("interpreted_for", None),
    ("candidates", None),
    ("candidates_error", None),
    ("fetched_for", None),
    ("ranked", None),
    ("ranked_for", None),
    ("explanation", None),
    ("explanation_error", None),
    ("explained_for", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── UI ────────────────────────────────────────────────────────────────────────
render_animation()

st.markdown('<div class="mw-eyebrow">AI Music Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="mw-title">How are you feeling?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="mw-subtitle">Describe your mood, your moment, your state of mind —<br>'
    "we'll find the music that fits.</div>",
    unsafe_allow_html=True,
)

mood_input = st.text_area(
    label="mood_input",
    placeholder="e.g. I'm exhausted after a long week and just want something warm and slow...",
    height=130,
    key="mood_text",
    label_visibility="collapsed",
)

submitted = st.button("Find My Music →")

if submitted:
    is_valid, guard_msg = validate_input(mood_input)
    if is_valid:
        clean = mood_input.strip()
        st.session_state.submitted_mood = clean
        st.session_state.mood_profile = None
        st.session_state.mood_profile_error = None
        st.session_state.interpreted_for = None
        st.session_state.candidates = None
        st.session_state.candidates_error = None
        st.session_state.fetched_for = None
        st.session_state.ranked = None
        st.session_state.ranked_for = None
        st.session_state.explanation = None
        st.session_state.explanation_error = None
        st.session_state.explained_for = None
        log_run_start(clean)
    else:
        log_validation_fail(mood_input, guard_msg)
        st.warning(guard_msg)

# ── Echo ──────────────────────────────────────────────────────────────────────
if st.session_state.submitted_mood:
    st.markdown(f"""
    <div class="mw-echo">
        <div class="mw-echo-label">Your mood</div>
        <div class="mw-echo-text">{st.session_state.submitted_mood}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Chapter 2: Interpret with LLM ────────────────────────────────────────────
if (
    st.session_state.submitted_mood
    and st.session_state.interpreted_for != st.session_state.submitted_mood
):
    loading_slot = st.empty()
    render_loading_animation(loading_slot)
    profile, error = interpret_mood(st.session_state.submitted_mood)
    loading_slot.empty()
    st.session_state.mood_profile = profile
    st.session_state.mood_profile_error = error
    st.session_state.interpreted_for = st.session_state.submitted_mood
    if profile:
        log_profile(profile)
    else:
        log_error("interpretation", error or "unknown")

if st.session_state.mood_profile_error:
    st.error(f"Could not interpret mood: {st.session_state.mood_profile_error}")

if st.session_state.mood_profile:
    render_profile_card(st.session_state.mood_profile)

# ── Chapter 3: Fetch from MusicBrainz ────────────────────────────────────────
if (
    st.session_state.mood_profile
    and st.session_state.fetched_for != st.session_state.interpreted_for
):
    with st.spinner("Searching the catalog..."):
        songs, error = fetch_candidates(st.session_state.mood_profile, limit=25)
        songs = enrich_candidates(songs)
        st.session_state.candidates = songs
        st.session_state.candidates_error = error
        st.session_state.fetched_for = st.session_state.interpreted_for
        log_retrieval(len(songs), error)

if st.session_state.candidates_error:
    st.warning(f"Catalog search: {st.session_state.candidates_error}")

if st.session_state.candidates:
    with st.expander(f"See all {len(st.session_state.candidates)} retrieved songs"):
        render_candidates_card(st.session_state.candidates)

# ── Chapter 4: Score & Rank ───────────────────────────────────────────────────
if (
    st.session_state.candidates
    and st.session_state.mood_profile
    and st.session_state.ranked_for != st.session_state.fetched_for
):
    with st.spinner("Ranking your results..."):
        ranked = rank_candidates(
            st.session_state.mood_profile,
            st.session_state.candidates,
            k=5,
        )
        if len(ranked) < 5:
            fallback_pool = fetch_mostloved()
            existing_keys = {
                (c.title.lower(), c.artist.lower())
                for c in st.session_state.candidates
            }
            new_candidates = [
                c for c in fallback_pool
                if (c.title.lower(), c.artist.lower()) not in existing_keys
            ]
            fallback_scored = [
                score_candidate(st.session_state.mood_profile, c)
                for c in new_candidates
            ]
            merged = sorted(ranked + fallback_scored, key=lambda s: s.score, reverse=True)
            ranked = merged[:5]
            logger.info(
                f"Fallback triggered: {len(new_candidates)} mostloved tracks added, "
                f"mood={st.session_state.mood_profile.mood}"
            )
        st.session_state.ranked = ranked
        st.session_state.ranked_for = st.session_state.fetched_for
        log_ranked(ranked)

if st.session_state.ranked:
    render_ranked_card(st.session_state.ranked)

# ── Chapter 5: LLM Explanation ────────────────────────────────────────────────
if (
    st.session_state.ranked
    and st.session_state.submitted_mood
    and st.session_state.mood_profile
    and st.session_state.explained_for != st.session_state.ranked_for
):
    with st.spinner("Writing your explanation..."):
        explanation, error = explain_recommendations(
            st.session_state.submitted_mood,
            st.session_state.mood_profile,
            st.session_state.ranked,
        )
        st.session_state.explanation = explanation
        st.session_state.explanation_error = error
        st.session_state.explained_for = st.session_state.ranked_for
        log_explanation(success=explanation is not None, error=error)

if st.session_state.explanation_error:
    st.error(f"Explanation: {st.session_state.explanation_error}")

if st.session_state.explanation:
    render_explanation_card(st.session_state.explanation)

# ── Chapter 5 Task 3: Follow-up refinement loop ───────────────────────────────
if st.session_state.explanation:
    st.markdown(
        '<div class="mw-followup-header">Not quite right? Describe it differently</div>',
        unsafe_allow_html=True,
    )
    followup_input = st.text_area(
        label="followup",
        placeholder="Try again — tell me more, narrow it down, or shift the mood...",
        height=100,
        key="followup_text",
        label_visibility="collapsed",
    )
    if st.button("Refine →", key="refine_btn"):
        is_valid, guard_msg = validate_input(followup_input)
        if is_valid:
            clean = followup_input.strip()
            st.session_state.submitted_mood = clean
            st.session_state.mood_profile = None
            st.session_state.mood_profile_error = None
            st.session_state.interpreted_for = None
            st.session_state.candidates = None
            st.session_state.candidates_error = None
            st.session_state.fetched_for = None
            st.session_state.ranked = None
            st.session_state.ranked_for = None
            st.session_state.explanation = None
            st.session_state.explanation_error = None
            st.session_state.explained_for = None
            log_run_start(clean)
            st.rerun()
        else:
            log_validation_fail(followup_input, guard_msg)
            st.warning(guard_msg)
